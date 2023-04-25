document.addEventListener('DOMContentLoaded', () => {
  var form = document.getElementById('download-form');
  var input = document.getElementById('url-input');
  var progress_bar = document.getElementById('progress-bar');
  
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    var url = input.value.trim();
    if (!url) {
      alert('Please enter a valid URL!');
      return;
    }

    fetch('/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'url': url
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'error') {
        alert('Error: ' + data.message);
      } else {
        progress_bar.style.width = '0%';
        window.location.href = data.redirect;
      }
    });
  });
});
