document.getElementById('toggleCheckbox').addEventListener('change', function() {
    var singleSelect = document.getElementById('singleSelect');
    var multiSelect = document.getElementById('multiSelect');
    var textElement = document.getElementById('toggleText');
  
    if (this.checked) {
        singleSelect.style.display = 'none';
        multiSelect.style.display = 'block';
    } else {
        singleSelect.style.display = 'block';
        multiSelect.style.display = 'none';
  
        // Clear all selections in multiSelect when switching to single selection
        var checkboxes = multiSelect.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false;
        });
    }
  });
  
  var selectedCitiesOrder = [];
  
  document.querySelectorAll('#multiSelect input[type="checkbox"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            selectedCitiesOrder.push(this.value);
        } else {
            selectedCitiesOrder = selectedCitiesOrder.filter(city => city !== this.value);
        }
        console.log('Selected Cities in Order:', selectedCitiesOrder);
    });
  });
  