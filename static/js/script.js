async function postData(url = "", data = {}) {
  const response = await fetch(url, {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
  });
  return response.json();
}

sendButton.addEventListener("click", async () => {
 let questionInput = document.getElementById("questionInput").value;
 if(!questionInput =="" ){
  document.getElementById("questionInput").value = "";
  document.querySelector(".right2").style.display = "block";
  document.querySelector(".right").style.display = "none";

  question1.innerHTML = questionInput;
  question2.innerHTML = questionInput;
  let result = await postData("/api", {
      "question": questionInput
  });
  solution.innerHTML = result.answer;
 }
 else{
  alert("enter somthing")
 }
});

sendButton2.addEventListener("click", async () => {
  let questionInput = document.getElementById("questionInput2").value;
  if(!questionInput == ""){
    console.log("hello")
    document.getElementById("questionInput2").value = "";

    question1.innerHTML = questionInput;
    question2.innerHTML = questionInput;
  
    let result = await postData("/api", {
        "question": questionInput
    });
    solution.innerHTML = result.answer;
  }
  else{
    alert("enter somthing")
   }
});

var cards = document.getElementsByClassName('card');

for (var i = 0; i < cards.length; i++) {
  cards[i].addEventListener('click', function() {
      updateInput(this.innerText);
  });
}

function updateInput(cardText) {
  var inputElement = document.getElementById('questionInput');
  inputElement.value = cardText.trim();
}

var spans1 = document.querySelectorAll('.history');
var inputTag1 = document.getElementById('questionInput');

spans1.forEach(function(span) {
  span.addEventListener('click', function() {
      inputTag1.value = span.textContent;
  });
});

var spans2 = document.querySelectorAll('.history');
var inputTag2 = document.getElementById('questionInput2');

spans2.forEach(function(span) {
  span.addEventListener('click', function() {
      inputTag2.value = span.textContent;
  });
});
function deleteChatItem() {
  // Get the chat container
  const chatContainer = document.querySelector('.chat-container');
  
  // Remove the chat container from the DOM
  chatContainer.remove();
}

