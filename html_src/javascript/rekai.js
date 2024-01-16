// --------------------------------------------------------------------------------------------
// JS for Copy Buttons

// Function to copy text from a specific element to clipboard and show a tooltip
function copyTextByElementId(elementId, buttonId) {
  var textToCopy = document.getElementById(elementId).textContent.trim();
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
    var originalJishoLink = this.href;
    if (localStorage.getItem("darkModeEnabled") === "true") {
      var modifiedJishoLink = originalJishoLink + "?color_theme=dark";
    } else {
      var modifiedJishoLink = originalJishoLink + "?color_theme=light";
    }
    iframe.src = modifiedJishoLink;
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

// --------------------------------------------------------------------------------------------
// JS for dark mode

function setDarkMode(isDarkModeEnabled) {
  var root = document.documentElement;
  if (isDarkModeEnabled) {
    root.classList.add("dark-mode");
    // reload jisho
    var jishoIframe = document.getElementById("sidebar-iframe");
    jishoIframe.src = "https://jisho.org/?color_theme=dark";
    localStorage.setItem("darkModeEnabled", true)

  } else {
    root.classList.remove("dark-mode");
    // reload jisho
    var jishoIframe = document.getElementById("sidebar-iframe");
    jishoIframe.src = "https://jisho.org/?color_theme=light";
    localStorage.setItem("darkModeEnabled", false)
  }
}

function toggleDarkMode() {
  var root = document.documentElement;
  var isDarkModeEnabled = root.classList.contains("dark-mode");

  // invert the boolean
  isDarkModeEnabled = !isDarkModeEnabled;

  // Call function that updates dark mode class on root
  setDarkMode(isDarkModeEnabled);
}

// Set initial dark mode state based on local storage
function initializeDarkMode() {
  var isDarkModeEnabled = localStorage.getItem("darkModeEnabled");

  if (isDarkModeEnabled) {
    setDarkMode(true);
  } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setDarkMode(true);
  } else {
    setDarkMode(false);
  }
}

// Call initializeDarkMode on page load
initializeDarkMode();

// --------------------------------------------------------------------------------------------

// JS for expanding and collapsing cards
function expandCollapseCard(cardID) {
  const masterCard = document.getElementById(cardID);
  const slaveCards = masterCard.querySelectorAll(".line-card-slave");

  slaveCards.forEach((slaveCard) => {
    slaveCard.classList.toggle("collapsed");

    if (slaveCard.classList.contains("collapsed")) {
      button = masterCard.querySelector(".expand-collapse-button");
      button.textContent = "Expand";
    } else {
      button = masterCard.querySelector(".expand-collapse-button");
      button.textContent = "Collapse";
    }
  });
}