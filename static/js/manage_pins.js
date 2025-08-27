// JS for manage_pins — moved out of template
document.addEventListener('DOMContentLoaded', function(){
  console.log('[manage_pins] DOMContentLoaded');
  const container = document.getElementById('manage-pins');
  if (!container) return;

  const toggleBase = container.dataset.toggleUrl; // e.g. /manage/pins/toggle/0/
  const deleteBase = container.dataset.deleteUrl; // e.g. /manage/pins/delete/0/
  const updateBase = container.dataset.updateUrl; // e.g. /manage/pins/update/0/

  function csrfHeaders() {
    return { 'X-CSRFToken': getCookie('csrftoken') };
  }

  document.querySelectorAll('.pin-toggle').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const url = toggleBase.replace('/0/', '/' + id + '/');
      fetch(url, { method: 'POST', headers: csrfHeaders() })
        .then(r => r.json())
        .then((j) => {
          showMessage('Statut PIN mis à jour', 'success');
          // update active text in DOM (handle both English "Active:" and French "Actif:")
          const li = btn.closest('li');
          if (li) {
            const info = li.querySelector('div > div');
            if (info) {
              const nowText = j.active ? 'Oui' : 'Non';
              info.textContent = info.textContent.replace(/(Active|Actif):\s*.*$/,'Actif: ' + nowText);
            }
          }
        })
        .catch(() => showMessage('Erreur mise à jour', 'error'));
    });
  });

  document.querySelectorAll('.pin-delete').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('[manage_pins] delete clicked for id=', btn.dataset.id);
      const id = btn.dataset.id;
      if (typeof window.confirmModal !== 'function') {
        console.warn('[manage_pins] confirmModal is not defined');
        showMessage('Impossible d\'afficher la modale de confirmation (confirmModal absent)', 'error');
        return;
      }
      window.confirmModal('Supprimer ce PIN ?', async () => {
        const url = deleteBase.replace('/0/', '/' + id + '/');
        try {
          const r = await fetch(url, { method: 'POST', headers: csrfHeaders() });
          if (!r.ok) { showMessage('Erreur suppression', 'error'); return; }
          showMessage('PIN supprimé', 'success');
          const li = btn.closest('li'); if (li) li.remove();
        } catch (err) { showMessage('Erreur suppression', 'error'); }
      });
    });
  });

  // Edit handler
  document.querySelectorAll('.pin-edit').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('[manage_pins] edit clicked for id=', btn.dataset.id);
      const id = btn.dataset.id;
      const li = btn.closest('li');
      const currentNameEl = li.querySelector('div > strong');
      const currentName = currentNameEl ? currentNameEl.textContent : '';
      if (typeof window.showFormModal !== 'function') {
        console.warn('[manage_pins] showFormModal is not defined');
        showMessage('Impossible d\'afficher le formulaire (showFormModal absent)', 'error');
        return;
      }
      window.showFormModal({
        title: 'Modifier PIN',
        fields: [
          { name: 'name', label: 'Nom', value: currentName },
          { name: 'pin', label: 'Nouveau code PIN (laisser vide pour garder)', type: 'password', value: '' }
        ],
        submitText: 'Enregistrer',
        onSubmit: async (data) => {
          const url = updateBase.replace('/0/', '/' + id + '/');
          const body = new URLSearchParams({ name: data.name || '' });
          if (data.pin) body.append('pin', data.pin);
          const res = await fetch(url, { method: 'POST', headers: Object.assign({'Content-Type':'application/x-www-form-urlencoded'}, csrfHeaders()), body: body.toString() });
          if (!res.ok) { const j = await res.json().catch(()=>null); showMessage((j && j.message) || 'Erreur mise à jour', 'error'); return; }
          const j = await res.json();
          showMessage('PIN mis à jour', 'success');
          if (li && j.pin) {
            if (currentNameEl) currentNameEl.textContent = j.pin.name;
            const info = li.querySelector('div > div');
            if (info) info.textContent = `Créé : ${new Date().toLocaleString()} — Actif : ${j.pin.active ? 'Oui' : 'Non'}`;
          }
        }
      });
    });
  });

  // client-side validation for create form (keeps previous behavior)
  const form = document.getElementById('pin-form');
  if (form) {
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const pinInput = document.getElementById('pin-raw');
      const nameInput = document.getElementById('pin-name');
      if (!pinInput) return;
      const pin = pinInput.value.trim();
      const name = nameInput ? nameInput.value.trim() : '';
      if (!pin) { showMessage('Veuillez entrer un PIN', 'error'); return; }
      if (!/^[0-9]+$/.test(pin)) { showMessage('Le PIN doit contenir uniquement des chiffres', 'error'); return; }
      if (pin.length < 4) { showMessage('Le PIN doit comporter au moins 4 chiffres', 'error'); return; }

      // AJAX submit
      fetch(window.location.pathname, {
        method: 'POST',
        headers: Object.assign({'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'}, csrfHeaders()),
        body: new URLSearchParams({ name: name, pin: pin }).toString()
      })
      .then(async (r) => {
        if (!r.ok) {
          const j = await r.json().catch(() => null);
          showMessage((j && j.errors && j.errors.join(', ')) || 'Erreur création', 'error');
          return;
        }
        const j = await r.json();
        // insert new row
        const ul = container.querySelector('ul');
          if (ul && j.pin) {
          const li = document.createElement('li');
          li.style = 'display:flex;justify-content:space-between;padding:0.6rem 0;border-bottom:1px solid #f1f5f9;align-items:center;';
          li.innerHTML = `<div><strong>${j.pin.name}</strong><div style="font-size:0.85rem;color:#6b7280">Créé : ${new Date(j.pin.created_at).toLocaleString()} — Actif : ${j.pin.active ? 'Oui' : 'Non'}</div></div><div style="display:flex;gap:0.5rem;align-items:center"><button class="pin-toggle" data-id="${j.pin.id}" style="padding:0.4rem 0.6rem;border-radius:6px;border:1px solid #e5e7eb;background:#fff;">Basculer</button><button class="pin-delete" data-id="${j.pin.id}" style="padding:0.4rem 0.6rem;border-radius:6px;border:1px solid #ef4444;background:#fff;color:#ef4444;">Supprimer</button></div>`;
          ul.insertBefore(li, ul.firstChild);
          // rebind events for new buttons
          const newToggle = li.querySelector('.pin-toggle');
          const newDelete = li.querySelector('.pin-delete');
          if (newToggle) newToggle.addEventListener('click', (e)=>{ e.preventDefault(); newToggle.disabled=true; const id=newToggle.dataset.id; const url=toggleBase.replace('/0/','/'+id+'/'); fetch(url,{method:'POST',headers:csrfHeaders()}).then(r=>r.json()).then((jj)=>{ showMessage('Statut PIN mis à jour','success'); // update active label on the new row
            const info = newToggle.closest('li') ? newToggle.closest('li').querySelector('div > div') : null; if (info && jj) info.textContent = info.textContent.replace(/(Active|Actif):\s*.*$/,'Actif: ' + (jj.active ? 'Oui' : 'Non')); newToggle.disabled=false;}).catch(()=>{showMessage('Erreur mise à jour','error'); newToggle.disabled=false;}); });
          if (newDelete) newDelete.addEventListener('click', (e)=>{ e.preventDefault(); const id=newDelete.dataset.id; window.confirmModal('Supprimer ce PIN ?', async () => { const url=deleteBase.replace('/0/','/'+id+'/'); try { const r = await fetch(url,{method:'POST',headers:csrfHeaders()}); if (!r.ok) { showMessage('Erreur suppression','error'); return; } showMessage('PIN supprimé','success'); li.remove(); } catch(err){ showMessage('Erreur suppression','error'); } }); });
          // also add an edit button bound to modal
          const editBtn = document.createElement('button'); editBtn.className='pin-edit'; editBtn.dataset.id = j.pin.id; editBtn.textContent='Modifier'; editBtn.style='padding:0.4rem 0.6rem;border-radius:6px;border:1px solid #e5e7eb;background:#fff;margin-left:0.5rem;';
          const actionsDiv = li.querySelector('div[style*="display:flex"]');
          if (actionsDiv) actionsDiv.appendChild(editBtn);
          if (editBtn) editBtn.addEventListener('click', (e)=>{ e.preventDefault(); const id=j.pin.id; const liRef = editBtn.closest('li'); const currentNameEl = liRef.querySelector('div > strong'); const currentName = currentNameEl ? currentNameEl.textContent : ''; window.showFormModal({ title: 'Modifier PIN', fields:[{name:'name',label:'Nom',value:currentName},{name:'pin',label:'Nouveau code PIN (laisser vide pour garder)',type:'password',value:''}], submitText:'Enregistrer', onSubmit: async (data)=>{ const url=updateBase.replace('/0/','/'+id+'/'); const body=new URLSearchParams({ name: data.name || '' }); if (data.pin) body.append('pin', data.pin); const res = await fetch(url, { method: 'POST', headers: Object.assign({'Content-Type':'application/x-www-form-urlencoded'}, csrfHeaders()), body: body.toString() }); if (!res.ok) { const j = await res.json().catch(()=>null); showMessage((j && j.message) || 'Erreur mise à jour', 'error'); return; } const jr = await res.json(); showMessage('PIN mis à jour', 'success'); if (liRef && jr.pin) { if (currentNameEl) currentNameEl.textContent = jr.pin.name; const info = liRef.querySelector('div > div'); if (info) info.textContent = `Créé : ${new Date().toLocaleString()} — Actif : ${jr.pin.active ? 'Oui' : 'Non'}`; } } }); });
        }
        pinInput.value=''; if (nameInput) nameInput.value='';
        showMessage('PIN créé', 'success');
      })
      .catch(() => showMessage('Erreur serveur', 'error'));
    });
  }
});
