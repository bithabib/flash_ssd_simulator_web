var form_id_js = "feedbackForm";

function js_onSuccess() {
  var feedbackMessage = document.getElementById("feedbackMessage");
  feedbackMessage.innerText = "Email Successfully Sent!";
  feedbackMessage.style.display = "block";
  document.getElementById(form_id_js).reset();
}

function js_onError(error) {
  var feedbackMessage = document.getElementById("feedbackMessage");
  feedbackMessage.innerText = "Email could not be sent.";
  feedbackMessage.style.display = "block";
}

var sendButton = document.getElementById("feedbackForm").querySelector("button[type='submit']");

function js_send(event) {
  event.preventDefault();

  sendButton.innerText = "Sending...";
  sendButton.disabled = true;

  var request = new XMLHttpRequest();
  request.onreadystatechange = function () {
    if (request.readyState == 4) {
      if (request.status == 200) {
        js_onSuccess();
      } else {
        js_onError(request.response);
      }
      sendButton.innerText = "Submit";
      sendButton.disabled = false;
    }
  };

  var name = document.getElementById("name").value;
  var email = document.getElementById("email").value;
  var message = document.getElementById("message").value;

  var data_js = {
    "access_token": "rp8thxqxvee0fpz3lvw6qr39",
    "subject": "User Feedback",
    "text": "Name: " + name + "\nEmail: " + email + "\nMessage: " + message
  };

  var params = toParams(data_js);

  request.open("POST", "https://postmail.invotes.com/send", true);
  request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

  request.send(params);
}

sendButton.addEventListener("click", js_send);

function toParams(data_js) {
  var form_data = [];
  for (var key in data_js) {
    form_data.push(encodeURIComponent(key) + "=" + encodeURIComponent(data_js[key]));
  }

  return form_data.join("&");
}