var form_id_js = "surveyForm";

function js_onSuccess() {
  var feedbackMessage = document.getElementById("feedbackMessage");
  feedbackMessage.innerText = "Survey responses successfully sent!";
  feedbackMessage.style.display = "block";
  document.getElementById(form_id_js).reset();
}

function js_onError(error) {
  var feedbackMessage = document.getElementById("feedbackMessage");
  feedbackMessage.innerText = "Error sending the survey responses.";
  feedbackMessage.style.display = "block";
}

var sendButton = document
  .getElementById(form_id_js)
  .querySelector("button[type='submit']");

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
  var profession = document.getElementById("profession").value;
  var satisfaction = document.getElementsByName("satisfaction")[0].value;
  var understandability =
    document.getElementsByName("understandability")[0].value;
  var simulatorRating = document.getElementsByName("simulator-rating")[0].value;
  var comments = document.getElementsByName("comments")[0].value;
  var conceptCoverage = document.querySelector(
    "input[name='concept-coverage']:checked"
  ).value;

  var data_js = {
    access_token: "rp8thxqxvee0fpz3lvw6qr39",
    subject: "SSD Simulator Feedback",
    text:
      "Name: " +
      name +
      "\nEmail: " +
      email +
      "\nProfession: " +
      profession +
      "\nSatisfaction: " +
      satisfaction +
      "\nUnderstandability: " +
      understandability +
      "\nSimulator Rating: " +
      simulatorRating +
      "\nComments: " +
      comments +
      "\nConcept Coverage: " +
      conceptCoverage,
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
    form_data.push(
      encodeURIComponent(key) + "=" + encodeURIComponent(data_js[key])
    );
  }

  return form_data.join("&");
}
