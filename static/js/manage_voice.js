document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('voice-form');
  if (!form) return;

  form.addEventListener('submit', function(e){
    e.preventDefault();
  const phrase = document.getElementById('phrase').value.trim();
  const action = document.getElementById('action').value;
    if (!phrase || !action) {
      showMessage('Phrase et action requises', 'error');
      return;
    }

    // AJAX submit
    fetch(window.location.pathname, {
      method: 'POST',
      headers: Object.assign({'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'}, {'X-CSRFToken': getCookie('csrftoken')}),
      body: new URLSearchParams({ phrase: phrase, action: action }).toString()
    })
    .then(async r => {
      if (!r.ok) {
        const j = await r.json().catch(()=>null);
        showMessage((j && j.errors && j.errors.join(', ')) || 'Erreur', 'error');
        return;
      }
      const j = await r.json();
      // insert into commands table
      const tbody = document.querySelector('table tbody');
      if (tbody && j.command) {
        const tr = document.createElement('tr');
        tr.style = 'border-bottom:1px solid #fafafa';
        tr.innerHTML = `<td>${j.command.phrase}</td><td>${j.command.action}</td><td style="width:180px"><button class="cmd-edit" data-id="${j.command.id}" style="margin-right:8px;padding:6px;border-radius:6px;border:1px solid #e5e7eb;background:#fff;">Edit</button><button class="cmd-delete" data-id="${j.command.id}" style="padding:6px;border-radius:6px;border:1px solid #ef4444;background:#fff;color:#ef4444;">Delete</button></td>`;
        tbody.insertBefore(tr, tbody.firstChild);
        document.getElementById('phrase').value=''; document.getElementById('action').value='';
        showMessage('Commande enregistrée', 'success');
        bindCommandRow(tr);
      }
    })
    .catch(()=> showMessage('Erreur serveur','error'));
  });
});

// Bind edit/delete handlers for existing rows
document.addEventListener('DOMContentLoaded', function(){
  const container = document.getElementById('manage-voice');
  if (!container) return;
  const updateBase = container.dataset.updateUrl;
  const deleteBase = container.dataset.deleteUrl;

  function csrfHeaders() { return {'X-CSRFToken': getCookie('csrftoken')}; }

  function bindCommandRow(row) {
    const edit = row.querySelector('.cmd-edit');
    const del = row.querySelector('.cmd-delete');
    if (edit) edit.addEventListener('click', async (e) => {
      e.preventDefault();
      const id = edit.dataset.id;
      const phraseCell = row.children[0];
      const actionCell = row.children[1];
      window.showFormModal({
        title: 'Modifier la commande',
        fields: [
          { name: 'phrase', label: 'Phrase', value: phraseCell.textContent },
          { name: 'action', label: 'Action', type: 'select', value: actionCell.textContent, options: ['open','close','toggle'] }
        ],
        submitText: 'Enregistrer',
        onSubmit: async (data) => {
          const url = updateBase.replace('/0/', '/' + id + '/');
          const res = await fetch(url, { method: 'POST', headers: Object.assign({'Content-Type':'application/x-www-form-urlencoded'}, csrfHeaders()), body: new URLSearchParams({ phrase: data.phrase, action: data.action }).toString() });
          if (!res.ok) { const j = await res.json().catch(()=>null); showMessage((j && j.errors && j.errors.join(', ')) || 'Erreur', 'error'); return; }
          const j = await res.json();
          phraseCell.textContent = j.command.phrase;
          actionCell.textContent = j.command.action;
          showMessage('Commande mise à jour', 'success');
        }
      });
    });
    if (del) del.addEventListener('click', async (e) => {
      e.preventDefault();
      const id = del.dataset.id;
      window.confirmModal('Supprimer cette commande ?', async () => {
        const url = deleteBase.replace('/0/', '/' + id + '/');
        const res = await fetch(url, { method: 'POST', headers: csrfHeaders() });
        if (!res.ok) { showMessage('Erreur suppression', 'error'); return; }
        row.remove();
        showMessage('Commande supprimée', 'success');
      });
    });
  }

  // bind existing rows
  document.querySelectorAll('table tbody tr').forEach(bindCommandRow);
});
