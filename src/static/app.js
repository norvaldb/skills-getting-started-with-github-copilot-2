document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and existing activities
      activitiesList.innerHTML = "";
      
      // Clear and reset the activity select dropdown
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants section using DOM manipulation to prevent XSS
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";
        
        const participantsTitle = document.createElement("p");
        const strongElement = document.createElement("strong");
        strongElement.textContent = "Current Participants:";
        participantsTitle.appendChild(strongElement);
        participantsSection.appendChild(participantsTitle);
        
        if (details.participants.length > 0) {
          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";
          
          details.participants.forEach(email => {
            const listItem = document.createElement("li");
            
            const emailSpan = document.createElement("span");
            emailSpan.className = "participant-email";
            emailSpan.textContent = email; // Using textContent prevents XSS
            
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.setAttribute("data-activity", name);
            deleteBtn.setAttribute("data-email", email);
            deleteBtn.setAttribute("title", "Remove participant");
            
            deleteBtn.innerHTML = `
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            `;
            
            listItem.appendChild(emailSpan);
            listItem.appendChild(deleteBtn);
            participantsList.appendChild(listItem);
          });
          
          participantsSection.appendChild(participantsList);
        } else {
          const noParticipantsMsg = document.createElement("p");
          noParticipantsMsg.className = "no-participants";
          noParticipantsMsg.textContent = "No participants yet. Be the first to sign up!";
          participantsSection.appendChild(noParticipantsMsg);
        }

        // Create activity card content using DOM manipulation to prevent XSS
        const titleElement = document.createElement("h4");
        titleElement.textContent = name; // Using textContent prevents XSS
        
        const descriptionElement = document.createElement("p");
        descriptionElement.textContent = details.description;
        
        const scheduleElement = document.createElement("p");
        const scheduleStrong = document.createElement("strong");
        scheduleStrong.textContent = "Schedule:";
        scheduleElement.appendChild(scheduleStrong);
        scheduleElement.appendChild(document.createTextNode(" " + details.schedule));
        
        const availabilityElement = document.createElement("p");
        const availabilityStrong = document.createElement("strong");
        availabilityStrong.textContent = "Availability:";
        availabilityElement.appendChild(availabilityStrong);
        availabilityElement.appendChild(document.createTextNode(" " + spotsLeft + " spots left"));
        
        activityCard.appendChild(titleElement);
        activityCard.appendChild(descriptionElement);
        activityCard.appendChild(scheduleElement);
        activityCard.appendChild(availabilityElement);
        activityCard.appendChild(participantsSection);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle participant deletion
  async function unregisterParticipant(activityName, email) {
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");

        // Refresh activities list
        await fetchActivities();

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to unregister participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering participant:", error);
    }
  }

  // Event delegation for delete buttons
  activitiesList.addEventListener("click", (event) => {
    const deleteBtn = event.target.closest(".delete-btn");
    if (deleteBtn) {
      const activityName = deleteBtn.getAttribute("data-activity");
      const email = deleteBtn.getAttribute("data-email");
      
      if (confirm(`Are you sure you want to unregister ${email} from ${activityName}?`)) {
        unregisterParticipant(activityName, email);
      }
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities list to show updated participants
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
