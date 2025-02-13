
let data;

// Function to send form data as JSON via XMLHttpRequest
function sendFormData(jsonData, route) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", route);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(jsonData);
    return xhr;
  }

// Function to submit the form
function submitHistoryForm() {
    const form = document.getElementById("updateChartForm"); 
    // Add event listener to the form's submit event
    form.addEventListener("submit", onSubmit); 
    function onSubmit(event) {
      event.preventDefault();
      form.removeEventListener("submit", onSubmit);
      
      const deviceName = document.getElementById("device-name").value;
      const startDate = document.getElementById("start-date").value;
      const endDate = document.getElementById("end-date").value;
      const jsonData = JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        device_name: deviceName
        });
        
      const xhr = sendFormData(jsonData,"/get-history");
      const spinner = document.querySelector(".spinner.center");
      
      // Handle the XMLHttpRequest response
      xhr.onreadystatechange = function () {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          const json = JSON.parse(this.responseText);
          if (json.status === "success") {
            // data = json.data;
            console.log("Status = OK")
            updateHistorySensorData(json.sensors_data)
          // } else {
          //   showError(json.message);
          }
          spinner.style.display = "none";
        }
      };
      spinner.style.display = "block";
    }
  }



