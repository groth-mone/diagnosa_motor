from django.shortcuts import render, redirect, get_object_or_404
from .models import Gejala, Rule, Diagnosa
from .forms import GejalaForm, DiagnosaForm, RuleForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
import json
from .utils import forward_chaining

@login_required
def dashboard(request):
    gejala_count = Gejala.objects.count()
    diagnosa_count = Diagnosa.objects.count()
    rule_count = Rule.objects.count()
    user_count = User.objects.count()
    return render(request, 'dashboard.html', {
        'gejala_count': gejala_count,
        'diagnosa_count': diagnosa_count,
        'rule_count': rule_count,
        'user_count': user_count,
    })

def index(request):
    gejala = Gejala.objects.all().order_by('nama')
    return render(request, 'index.html', {'gejala': gejala})

def proses_diagnosa(request):
    if request.method == 'POST':
        selected_gejala_ids = request.POST.getlist('gejala')
        
        if not selected_gejala_ids:
            return redirect('index')
            
        selected_set = set(map(int, selected_gejala_ids))

        rules = Rule.objects.select_related('diagnosa').all()
        best_match = None
        best_accuracy = 0

        for rule in rules:
            rule_gejala_ids = set(map(int, rule.gejala_ids.split(',')))

            if rule_gejala_ids == selected_set:
                return render(request, 'hasil.html', {
                    'diagnosa': rule.diagnosa,
                    'akurasi': 100,
                    'gejala_terpilih': Gejala.objects.filter(id__in=selected_set),
                })
            else:
                match_count = len(selected_set & rule_gejala_ids)
                total_rule_gejala = len(rule_gejala_ids)
                
                if match_count > 0:
                    accuracy = round((match_count / total_rule_gejala) * 100, 2)
                    
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_match = rule

        if best_match:
            return render(request, 'hasil.html', {
                'diagnosa': best_match.diagnosa,
                'akurasi': best_accuracy,
                'gejala_terpilih': Gejala.objects.filter(id__in=selected_set),
            })

        default_diagnosa = Diagnosa.objects.first()
        
        Rule.objects.create(
            diagnosa=default_diagnosa,
            gejala_ids=",".join(selected_gejala_ids)
        )

        return render(request, 'hasil.html', {
            'diagnosa': default_diagnosa,
            'akurasi': 0,
            'gejala_terpilih': Gejala.objects.filter(id__in=selected_set),
            'info': "Pengetahuan baru telah ditambahkan sebagai rule baru.",
        })
    return redirect('index')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard.html')
        else:
            context = {'error': 'Username atau password salah'}
            return render(request, 'login.html', context)
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

# API endpoint untuk mendapatkan diagnosa via AJAX (opsional)
def api_diagnosa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_gejala_ids = data.get('gejala_ids', [])
        
        if not selected_gejala_ids:
            return JsonResponse({'error': 'Tidak ada gejala yang dipilih'}, status=400)
            
        selected_set = set(map(int, selected_gejala_ids))
        rules = Rule.objects.select_related('diagnosa').all()
        best_match = None
        best_accuracy = 0

        for rule in rules:
            rule_gejala_ids = set(map(int, rule.gejala_ids.split(',')))

            if rule_gejala_ids == selected_set:
                diagnosa = rule.diagnosa
                return JsonResponse({
                    'diagnosa_nama': diagnosa.nama,
                    'diagnosa_solusi': diagnosa.solusi,
                    'akurasi': 100,
                    'gejala_terpilih': list(selected_set),
                })
            else:
                match_count = len(selected_set & rule_gejala_ids)
                if match_count > 0:
                    accuracy = round((match_count / len(rule_gejala_ids)) * 100, 2)
                    if accuracy > best_accuracy:
                        best_accuracy = accuracy
                        best_match = rule

        if best_match:
            diagnosa = best_match.diagnosa
            return JsonResponse({
                'diagnosa_nama': diagnosa.nama,
                'diagnosa_solusi': diagnosa.solusi,
                'akurasi': best_accuracy,
                'gejala_terpilih': list(selected_set),
            })
        default_diagnosa = Diagnosa.objects.first()
        
        Rule.objects.create(
            diagnosa=default_diagnosa,
            gejala_ids=",".join(map(str, selected_set))
        )

        return JsonResponse({
            'diagnosa_nama': default_diagnosa.nama,
            'diagnosa_solusi': default_diagnosa.solusi,
            'akurasi': 0,
            'gejala_terpilih': list(selected_set),
            'info': "Pengetahuan baru telah ditambahkan sebagai rule baru.",
        })
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def hasil_diagnosa(request):
    selected_gejala = request.session.get('selected_gejala', [])  # misalnya [1, 3]

    if not selected_gejala:
        return redirect('index')

    all_rules = list(Rule.objects.all().values('id', 'diagnosa_id', 'gejala_ids'))
    gejala_str = ",".join(map(str, sorted(selected_gejala)))
    existing_rule = Rule.objects.filter(gejala_ids=gejala_str).first()

    if existing_rule:
        diagnosa = Diagnosa.objects.get(id=existing_rule.diagnosa_id)
        akurasi = 100
        info = None
    else:
        best_match, saran_gejala_ids = forward_chaining(selected_gejala, all_rules)
        if best_match:
            diagnosa = Diagnosa.objects.get(id=best_match['rule']['diagnosa_id'])
            akurasi = best_match['akurasi']
            saran_gejala = Gejala.objects.filter(id__in=saran_gejala_ids)
            saran_nama = [g.nama for g in saran_gejala]
            info = f"Pertimbangkan untuk memeriksa gejala tambahan: {', '.join(saran_nama)} untuk hasil yang lebih akurat."

            # Simpan rule baru (opsional: hanya jika akurasi cukup)
            if akurasi >= 60:
                Rule.objects.create(diagnosa=diagnosa, gejala_ids=gejala_str)
        else:
            diagnosa = Diagnosa(nama="Tidak Diketahui", solusi="Data tidak mencukupi untuk menentukan diagnosa.")
            akurasi = 0
            info = "Tidak ditemukan kecocokan dengan pengetahuan yang ada."

    gejala_terpilih = Gejala.objects.filter(id__in=selected_gejala)

    return render(request, 'hasil_diagnosa.html', {
        'diagnosa': diagnosa,
        'akurasi': akurasi,
        'info': info,
        'gejala_terpilih': gejala_terpilih
    })

@login_required
def gejala_list(request):
    query = request.GET.get('q')
    if query:
        data = Gejala.objects.filter(nama__icontains=query)
    else:
        data = Gejala.objects.all()
    return render(request, 'gejala_list.html', {'data': data})

@login_required
def gejala_add(request):
    form = GejalaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('gejala_list')
    return render(request, 'form.html', {'form': form, 'title': 'Tambah Gejala'})

@login_required
def gejala_edit(request, pk):
    obj = get_object_or_404(Gejala, pk=pk)
    form = GejalaForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('gejala_list')
    return render(request, 'form.html', {'form': form, 'title': 'Edit Gejala'})

@login_required
def gejala_delete(request, pk):
    obj = get_object_or_404(Gejala, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect('gejala_list')
    return render(request, 'confirm_delete.html', {'object': obj})

@login_required
def rule_list(request):
    rules = Rule.objects.all()
    return render(request, 'rule_list.html', {'rules': rules})

@login_required
def rule_create(request):
    if request.method == 'POST':
        form = RuleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rule_list')
    else:
        form = RuleForm()
    return render(request, 'form.html', {'form': form, 'title': 'Create Rule'})

@login_required
def rule_edit(request, pk):
    obj = get_object_or_404(Rule, pk=pk)
    form = RuleForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('rule_list')
    return render(request, 'form.html', {'form': form, 'title': 'Edit Rule'})

@login_required
def rule_delete(request, pk):
    rule = Rule.objects.get(pk=pk)
    if request.method == "POST":
        rule.delete()
        return redirect('rule_list')
    return render(request, 'confirm_delete.html', {'object': rule})

@login_required
def diagnosa_list(request):
    diagnosas = Diagnosa.objects.all()
    return render(request, 'diagnosa_list.html', {'diagnosas': diagnosas})

@login_required
def diagnosa_create(request):
    if request.method == 'POST':
        form = DiagnosaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('diagnosa_list')
    else:
        form = DiagnosaForm()
    return render(request, 'form.html', {'form': form})

@login_required
def diagnosa_update(request, pk):
    diagnosa = get_object_or_404(Diagnosa, pk=pk)
    if request.method == 'POST':
        form = DiagnosaForm(request.POST, instance=diagnosa)
        if form.is_valid():
            form.save()
            return redirect('diagnosa_list')
    else:
        form = DiagnosaForm(instance=diagnosa)
    return render(request, 'form.html', {'form': form})

@login_required
def diagnosa_delete(request, pk):
    diagnosa = get_object_or_404(Diagnosa, pk=pk)
    if request.method == 'POST':
        diagnosa.delete()
        return redirect('diagnosa_list')
    return render(request, 'confirm_delete.html', {'diagnosa': diagnosa})

def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func

@admin_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'form.html', {'form': form})

@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'form.html', {'form': form})

@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'confirm_delete.html', {'user': user})