document.addEventListener('DOMContentLoaded', function () {
  const input = document.querySelector('input[type="file"][name="image"]');
  if (!input) return;
  const preview = document.createElement('div');
  preview.className = 'mt-3';
  input.parentNode.appendChild(preview);
  input.addEventListener('change', function (e) {
    preview.innerHTML = '';
    const file = e.target.files[0];
    if (!file) return;
    const img = document.createElement('img');
    img.style.maxWidth = '200px';
    img.style.borderRadius = '8px';
    img.src = URL.createObjectURL(file);
    preview.appendChild(img);
  });
});
