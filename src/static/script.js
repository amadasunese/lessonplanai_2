// Keep track of the total number of sections
const totalSections = 15; 
let currentSection = 1; 

function showSection(sectionId) {
    // Collapse the current section (if not the first)
    if (currentSection > 1) { 
        const previousId = "section" + (currentSection - 1);
        $("#" + previousId).hide(); 
    }

    $("#" + sectionId).show();
    updateProgressBar();
    currentSection++; 
}

function updateProgressBar() {
    const percentage = ((currentSection - 1) / totalSections) * 100;
    $(".progress-bar").css("width", percentage + "%");
    $(".progress-bar").attr("aria-valuenow", percentage);
}

// Event Listeners for "Next" buttons
$("#nextStep1").click(function () {
    showSection("nameSection");
});

// Add similar event listeners for the rest of your "Next" buttons 
// Example:
$("#nextStep2").click(function() {
  populateName();
  showSection("detailsSection"); 
});
