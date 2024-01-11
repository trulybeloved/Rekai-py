// --------------------------------------------------------------------------------------------
// JS for Copy Buttons

// Function to copy text from a specific element to clipboard and show a tooltip
function copyTextByElementId(elementId, buttonId) {
  var textToCopy = document.getElementById(elementId).textContent;
  var copyButton = document.getElementById(buttonId);
  navigator.clipboard.writeText(textToCopy);

  showTooltip(copyButton, "Copied!");
}

// --------------------------------------------------------------------------------------------
// JS for Tooltip

// Function to show a tooltip with a message
function showTooltip(element, message) {
  const tooltip = document.createElement("div");
  tooltip.textContent = message;
  tooltip.style.position = "absolute";
  tooltip.style.background = "black";
  tooltip.style.color = "white";
  tooltip.style.padding = "5px 10px";
  tooltip.style.borderRadius = "5px";
  tooltip.style.fontSize = "10px";
  tooltip.style.whiteSpace = "nowrap";
  tooltip.style.transform = "translateY(-100%)";
  tooltip.style.top = `${element.offsetTop - 10}px`;
  tooltip.style.left = `${element.offsetLeft - 8}px`;
  tooltip.style.zIndex = "2000";

  element.parentElement.appendChild(tooltip);

  // Remove the tooltip after 1.2 seconds
  setTimeout(() => {
    tooltip.remove();
  }, 1200); // Remove after 1.2 seconds
}

// --------------------------------------------------------------------------------------------
// JS for Jisho Links

// Select all elements with class 'jisho-link'
var jishoLinks = document.querySelectorAll(".jisho-link");

// Attach a click event to each Jisho link to update the src of an iframe
jishoLinks.forEach(function (jishoLink) {
  jishoLink.onclick = function (event) {
    event.preventDefault();
    var iframe = document.getElementById("sidebar-iframe");
    iframe.src = this.href;
  };
});

// --------------------------------------------------------------------------------------------
// JS for Audio Buttons

// Select all elements with class 'audioButton'
var audioButtons = document.querySelectorAll(".audioButton");
var currentlyPlaying = null; // To keep track of the audio that's currently playing

// Attach click and ended events to each audio button and player
audioButtons.forEach(function (audioButton, index) {
  var audioPlayer = document.querySelectorAll(".audioPlayer")[index];
  audioPlayer.previousButton = audioButton; // assigns the currently playing button as the previously clicked button

  audioButton.addEventListener("click", function () {
    // If another audio is playing, pause and reset it
    if (currentlyPlaying && currentlyPlaying !== audioPlayer) {
      resetButtonState(currentlyPlaying.previousButton);
      currentlyPlaying.pause();
      currentlyPlaying.currentTime = 0;
      currentlyPlaying = null;
    }

    // Toggle between playing and pausing
    if (audioPlayer.paused) {
      audioPlayer.play();
      currentlyPlaying = audioPlayer;
      // change button appearance to that of a stop button when audio is playing
      updateButtonState(
        audioButton,
        "◼ TTS",
        "audioButton audioButton-stop"
      );
    } else {
      // While audio is playing and the user clicks on the stop button assigned to the currently playing audio, stop playback and reset state
      audioPlayer.pause();
      audioPlayer.currentTime = 0;
      currentlyPlaying = null;
      resetButtonState(audioButton);
    }
  });

  audioPlayer.addEventListener("ended", function () {
    resetButtonState(audioButton);
    currentlyPlaying = null;
  });
});

// Function to update the button state with new text and class
function updateButtonState(button, newText, newClassName) {
  button.textContent = newText;
  button.className = newClassName;
}

// Function to reset the button state to default
function resetButtonState(button) {
  var defaultText = "▶ TTS";
  var defaultClassName = "audioButton audioButton-play";

  updateButtonState(button, defaultText, defaultClassName);
}

// Set initial button state to default for all audio buttons
audioButtons.forEach(function (audioButton) {
  resetButtonState(audioButton);
});

// --------------------------------------------------------------------------------------------
// JS for Top Bar Toggle Buttons

function toggleElementDisplay(buttonId, elementClass, displayType, showText, hideText) {
  var containers =
    document.querySelectorAll(elementClass);
  containers.forEach(function (container) {
    if (container.style.display === "none") {
      container.style.display = displayType;
    } else {
      container.style.display = "none";
    }
  });

  var button = document.getElementById(buttonId);
  if (containers[0].style.display === "none") {
    button.textContent = showText;
  } if (containers[0].style.display !== "none") {
    button.textContent = hideText;
  }
}

function toggleRightSidebar() {
  const root = document.documentElement;
  const rightSidebarContainer = document.getElementById("right-sidebar");
  const toggleSidebarButton = document.getElementById("toggle-sidebar-button");

  if (rightSidebarContainer.classList.contains('sidebar-expanded')) {
    root.style.setProperty('--sidbar-percent-width', '0%');
    root.style.setProperty('--sidebar-display', 'none');
    toggleSidebarButton.textContent = "Show OmniBar";
    rightSidebarContainer.className = "right-sidebar sidebar-collapsed";
  } else  {
    root.style.setProperty('--sidbar-percent-width', '33%');
    root.style.setProperty('--sidebar-display', 'block');
    toggleSidebarButton.textContent = "Hide OmniBar";
    rightSidebarContainer.className = "right-sidebar sidebar-expanded";
  }
}

