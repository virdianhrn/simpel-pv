from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TahunAnggaran
from .forms import TahunAnggaranForm
from accounts.decorators import admin_required

@admin_required
def manage_tahun_anggaran(request):
    if request.method == 'POST':
        if 'add_new_year' in request.POST:
            form = TahunAnggaranForm(request.POST)
            if form.is_valid():
                # First, save the new object
                saved_tahun = form.save()
                
                # NOW, check if the admin set the new year to be active
                if saved_tahun.status == TahunAnggaran.StatusChoices.AKTIF:
                    # If so, deactivate all OTHER active years
                    TahunAnggaran.objects.filter(status=TahunAnggaran.StatusChoices.AKTIF).exclude(pk=saved_tahun.pk).update(status=TahunAnggaran.StatusChoices.DITUTUP)
                
                messages.success(request, f"Tahun Anggaran {saved_tahun.tahun} berhasil ditambahkan.")
            else:
                messages.error(request, "Gagal menambahkan tahun anggaran baru. Mohon periksa input Anda.")

        elif 'update_status' in request.POST:
            tahun_id = request.POST.get('tahun_id')
            new_status = request.POST.get('update_status')
            
            try:
                tahun_to_update = TahunAnggaran.objects.get(pk=tahun_id)
                if new_status == TahunAnggaran.StatusChoices.AKTIF:
                    TahunAnggaran.objects.filter(status=TahunAnggaran.StatusChoices.AKTIF).exclude(pk=tahun_to_update.pk).update(status=TahunAnggaran.StatusChoices.DITUTUP)
                
                tahun_to_update.status = new_status
                tahun_to_update.save()
                messages.success(request, f"Status untuk Tahun Anggaran {tahun_to_update.tahun} berhasil diperbarui.")
            except TahunAnggaran.DoesNotExist:
                messages.error(request, "Tahun Anggaran tidak ditemukan.")
        
        return redirect('konfigurasi:manage_tahun_anggaran')

    # For GET requests (logic remains the same)
    tahun_anggaran_list = TahunAnggaran.objects.all().order_by('-tahun')
    form = TahunAnggaranForm()
    context = {
        'tahun_anggaran_list': tahun_anggaran_list,
        'form': form,
    }
    return render(request, 'manage_tahun_anggaran.html', context)