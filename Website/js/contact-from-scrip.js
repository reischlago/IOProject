var scriptURL = 'https://script.google.com/macros/s/AKfycbw9a5vpIAEPJetYikfbRZ2nmXOiOqk8uIEmGRGfqMttXe87_a0wQneG5mTHe4G0MKyuDw/exec'
var form = document.forms['submit-to-google-sheet']
var successMessage = document.getElementById('success-message');
var sendingMessage = document.getElementById('sending-message');
form.addEventListener('submit', function(e) {
    e.preventDefault()
    form.style.display = 'none'; // hide the form immediately
    sendingMessage.style.display = 'block'; // show the sending message
    fetch(scriptURL, { method: 'POST', body: new FormData(form) })
        .then(function(response) {
            console.log('Success!', response)
            sendingMessage.style.display = 'none'; // hide the sending message
            successMessage.style.display = 'block'; // show the success message
        })
        .catch(function(error) {
            console.error('Error!', error.message)
            form.style.display = 'block'; // show the form again in case of error
            sendingMessage.style.display = 'none'; // hide the sending message
        })
})
