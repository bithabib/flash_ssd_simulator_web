const form = document.getElementById("feedback-form");
const commentsContainer = document.getElementById("comments-container");

form.addEventListener("submit", function (e) {
  e.preventDefault();

  const feedbackInput = document.getElementById("feedback-input");
  const feedbackText = feedbackInput.value.trim();

  if (feedbackText !== "") {
    const comment = createComment(feedbackText);
    commentsContainer.prepend(comment);

    feedbackInput.value = "";
  }
});

function createComment(text) {
  const comment = document.createElement("div");
  comment.classList.add("comment");

  const avatar = document.createElement("img");
//   avatar.src = "../src/logo/user.jpg";
  avatar.alt = "User Avatar";

  const commentContent = document.createElement("div");
  commentContent.classList.add("comment-content");

  const username = document.createElement("h3");
  username.textContent = "User";

  const commentText = document.createElement("p");
  commentText.textContent = text;

  commentContent.appendChild(username);
  commentContent.appendChild(commentText);

  const commentActions = document.createElement("div");
  commentActions.classList.add("comment-actions");

  const likeButton = document.createElement("div");
  likeButton.classList.add("like-button");
  likeButton.innerHTML = '<i class="fas fa-thumbs-up"></i>Like';

  const likeCount = document.createElement("span");
  likeCount.classList.add("like-count");
  likeCount.textContent = "0";

  commentActions.appendChild(likeButton);
  commentActions.appendChild(likeCount);

  comment.appendChild(avatar);
  comment.appendChild(commentContent);
  comment.appendChild(commentActions);

  return comment;
}
