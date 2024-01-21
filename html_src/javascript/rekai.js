// --------------------------------------------------------------------------------------------
// JS for Copy Buttons

// Function to copy text from a specific element to clipboard and show a tooltip
function copyTextByElementId(elementId, buttonId) {
  var textToCopy = document.getElementById(elementId).textContent.trim();
  var copyButton = document.getElementById(buttonId);
  navigator.clipboard.writeText(textToCopy);

  showTooltip(copyButton, "Copied!");
}

var copyableElements = document.querySelectorAll(".copy-on-click");

copyableElements.forEach(function (copyableElement) {

  copyableElement.addEventListener("keydown", function (event) {
    if (event.ctrlKey || event.metaKey) {
      handleMouseOver(event, this);
      this.focus();
    }
  });

  copyableElement.addEventListener("keyup", function (event) {
    handleMouseOut(event, this);
    this.focus();
  });

  copyableElement.addEventListener("mouseover", function (event) {
    copyableElement.setAttribute("tabindex", "0");
    this.focus();
    handleMouseOver(event, this);
  });

  copyableElement.addEventListener("mouseout", function (event) {
    handleMouseOut(event, this);
    this.removeAttribute("tabindex");
  });

  copyableElement.addEventListener("click", function (event) {
    copyTextOnClick(event, this);
  });

})


function copyTextOnClick(event, element) {
  // Check if the Control (or Command) key is pressed
  if (event.ctrlKey || event.metaKey) {
    var textToCopy = element.textContent.trim();
    navigator.clipboard.writeText(textToCopy);
    showTooltip(element, "Copied!");
  }
}

function handleMouseOver(event, element) {
  if (event.ctrlKey || event.metaKey) {
    element.classList.add("hovered");
  }
}

function handleMouseOut(event, element) {
    element.classList.remove("hovered");
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
  tooltip.style.top = `${element.offsetTop - tooltip.offsetHeight - 10}px`;
  tooltip.style.left = `${element.offsetLeft + element.offsetWidth/4}px`;
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



// --------------------------------------------------------------------------------------------
// JS for Top Bar Toggle Buttons
function updateButtonClasses() {
  const toggleButtons = document.querySelectorAll(".top-bar-button");
  toggleButtons.forEach(function (toggleButton) {
    toggleButton.classList.add("toggle-button-enabled");
  });
}

updateButtonClasses();

function toggleDisplay(button, elementClass, displayType) {
  
  elements = document.querySelectorAll(elementClass);
  elements.forEach(function (element) {
    if (element.style.display === "none") {
      element.style.display = displayType;
      button.classList.add("toggle-button-enabled");
    } else {
      element.style.display = "none";
      button.classList.remove("toggle-button-enabled");
    }
  });
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
  const paraCard = document.getElementById(cardID);
  const lineCards = paraCard.querySelectorAll(".line-card-container");

  lineCards.forEach((lineCard) => {
    lineCard.classList.toggle("collapsed");

    if (lineCard.classList.contains("collapsed")) {
      lineCard.style.maxHeight = "0px";
      button = paraCard.querySelector(".expand-collapse-button");
      button.textContent = "Expand";
    } else {
      lineCard.style.maxHeight = lineCard.scrollHeight + 1000 + "px";
      button = paraCard.querySelector(".expand-collapse-button");
      button.textContent = "Collapse";
    }
  });
}

function expandCollapseLineContents(lineID) {
  const line = document.getElementById(lineID);
  const lineContent = line.querySelector(".line-card-contents-container");
  var computedStyle = getComputedStyle(lineContent);

  if (computedStyle.maxHeight === "0px") {
    lineContent.style.maxHeight = lineContent.scrollHeight + 1000 + "px";
  }

  lineContent.classList.toggle("collapsed");

  if (lineContent.classList.contains("collapsed")) {
    lineContent.style.maxHeight = "0px";  
  } else {
    lineContent.style.maxHeight = lineContent.scrollHeight + 1000 + "px";
  }
  };



// --------------------------------------------------------------------------------------------
// JS for wavesurfer audio player and audiobuttons

var audioButtons = document.querySelectorAll(".audioButton");

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

document.addEventListener('DOMContentLoaded', () => {
  const lineCards = document.querySelectorAll('.line-card');
  let currentlyPlayingWaveSurfer = null;

  function updateButtonState(button, newText, newClassName) {
    button.textContent = newText;
    button.className = newClassName;
  }

  function resetButtonState(button) {
    var defaultText = "▶ TTS";
    var defaultClassName = "audioButton audioButton-play";
    updateButtonState(button, defaultText, defaultClassName);
  }

  lineCards.forEach((container, index) => {
    const audioElement = container.querySelector('.audioPlayer');
    const waveformContainer = container.querySelector('.audio-waveform');
    const audioBase64Ogg = audioElement.getAttribute('base64ogg');

    // Create a Blob from the base64 data
    var binaryData = atob(audioBase64Ogg);
    var arrayBuffer = new ArrayBuffer(binaryData.length);
    var view = new Uint8Array(arrayBuffer);
    for (var i = 0; i < binaryData.length; i++) {
        view[i] = binaryData.charCodeAt(i);
    }
    var blob = new Blob([arrayBuffer], { type: 'audio/ogg' });

    // Create an Object URL from the Blob
    audio_url = URL.createObjectURL(blob);

    // Create the waveform
    const wavesurfer = WaveSurfer.create({
      container: waveformContainer,
      waveColor: "#7B7B7B",
      progressColor: "#AFFF9B",
      barWidth: 1,
      url: audio_url,
      responsive: true,
      height: 30,
      hideScrollbar: true,
      cursorWidth: 0,
      audioRate: 1,
      autoplay: false,
    });

    // Play/pause on button click
    const audioButton = container.querySelector('.audioButton');
    audioButton.addEventListener('click', () => {
      if (currentlyPlayingWaveSurfer && currentlyPlayingWaveSurfer !== wavesurfer) {
        currentlyPlayingWaveSurfer.stop();
        resetButtonState(currentlyPlayingAudioButton);
      }

      if (wavesurfer.isPlaying()) {
        wavesurfer.stop();
        currentlyPlayingWaveSurfer = null;
        resetButtonState(audioButton);
      } else {
        wavesurfer.play();
        currentlyPlayingWaveSurfer = wavesurfer;
        currentlyPlayingAudioButton = audioButton;
        updateButtonState(audioButton, "◼ TTS", "audioButton audioButton-stop");
      }
    });

    wavesurfer.on('finish', () => {
      if (currentlyPlayingWaveSurfer === wavesurfer) {
        currentlyPlayingWaveSurfer = null;
        resetButtonState(audioButton);
      }  

    })
  });
});

// JS for highlighting the last clicked para card
document.addEventListener('DOMContentLoaded', function() {
  var paraCards = document.querySelectorAll('.para-card');

  paraCards.forEach(function(paraCard) {
      paraCard.addEventListener('click', function() {
          // Remove 'clicked' class from all paracards
          paraCards.forEach(function(d) {
              d.classList.remove('clicked');
          });

          // Add 'clicked' class to the clicked div
          paraCard.classList.add('clicked');
      });
  });
});