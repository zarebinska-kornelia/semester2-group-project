// Get the map container and the modal
const map = document.getElementById('map');
const markerModal = new bootstrap.Modal(document.getElementById('markerModal'));
const xCoordInput = document.getElementById('x-coord');
const yCoordInput = document.getElementById('y-coord');

// Event listener for clicks on the map to open the modal form
map.addEventListener('click', function(event) {
    const mapRect = map.getBoundingClientRect();
    const xPercent = ((event.clientX - mapRect.left) / mapRect.width) * 100;
    const yPercent = ((event.clientY - mapRect.top) / mapRect.height) * 100;

    document.getElementById('markerModalLabel').textContent = 'Add Marker';
    document.getElementById('marker-form').action = '/add_marker';
    document.getElementById('marker-text').value = '';
    const submitButton = document.querySelector('#marker-form button[type="submit"]');
    submitButton.textContent = 'Add Marker';  // Change button text
    submitButton.classList.remove('btn-danger');
    submitButton.classList.add('btn-primary');
    // Set the coordinates in the form
    xCoordInput.value = xPercent.toFixed(2);
    yCoordInput.value = yPercent.toFixed(2);

    // Show the Bootstrap modal
    markerModal.show();
});

function handleMarkerClick(markerId, markerText, isItAnAdmin, isItComplete) {
    if (isItAnAdmin === true) {
        handleAdminMarkerClick(markerId, markerText)
    }
    else {
        // Regular users mark the marker as "complete" (change color to blue)
            fetch(`/complete_marker/${markerId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}'  // If you use CSRF protection
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("line 36 success, response is coming back");
                    // Change the marker color to blue on the front end
                    const markerElement = document.querySelector(`[data-marker-id='${markerId}']`)
                    if (markerElement) {
                        console.log("line 41 success, element is created and exists");
                        if (isItComplete === true) {
                            console.log("makes it red")
                            markerElement.style.backgroundColor = 'red';
                            markerElement.onclick = function() {
                                handleMarkerClick(markerId, markerText, isItAnAdmin, false);
                            }
                        }
                        else {
                            console.log("makes it blue")
                            markerElement.style.backgroundColor = 'blue';
                            markerElement.onclick = function() {
                                handleMarkerClick(markerId, markerText, isItAnAdmin, true);
                            }
                        }
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }

}

function handleAdminMarkerClick(markerId, markerText) {
        document.getElementById('markerModalLabel').textContent = 'Delete Marker';
        document.getElementById('marker-form').action = '/delete_marker';  // Change form action to deletion
        // Add the marker ID to a hidden input
        let markerIdInput = document.getElementById('marker-id');
        if (!markerIdInput) {
            markerIdInput = document.createElement('input');
            markerIdInput.type = 'hidden';
            markerIdInput.name = 'marker_id';
            markerIdInput.id = 'marker-id';
            document.getElementById('marker-form').appendChild(markerIdInput);
        }
        markerIdInput.value = markerId;

        // (Optional) If you want to show the marker's text in the modal, populate the textarea
        document.getElementById('marker-text').value = markerText;

        // Adjust the modal buttons for deletion
        const submitButton = document.querySelector('#marker-form button[type="submit"]');
        submitButton.textContent = 'Delete Marker';  // Change button text
        submitButton.classList.remove('btn-primary');
        submitButton.classList.add('btn-danger');

        // Show the modal
        markerModal.show();
}