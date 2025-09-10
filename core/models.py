from django.db import models

class Gejala(models.Model):
    kode = models.CharField(max_length=10)
    nama = models.TextField()

    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Diagnosa(models.Model):
    kode = models.CharField(max_length=10)
    nama = models.TextField()
    solusi = models.TextField()

    def __str__(self):
        return f"{self.kode} - {self.nama}"

class Rule(models.Model):
    diagnosa = models.ForeignKey(Diagnosa, on_delete=models.CASCADE)
    gejala_ids = models.TextField()  # Format: "1,4,5"

    def __str__(self):
        return f"Rule untuk {self.diagnosa.nama}"

