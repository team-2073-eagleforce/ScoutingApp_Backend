var params = new URLSearchParams(window.location.search)
if (params.get("code") == null) {
    window.location.replace(`/analysis/team?code=${localStorage.getItem('comp')}`)
}

function sortTable(table_to_sort){
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById(table_to_sort);
    switching = true;

    while (switching) {
        // Start by saying: no switching is done:
        switching = false;
        rows = table.rows;

        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false;
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("DIV")[0];
            y = rows[i + 1].getElementsByTagName("DIV")[0];
            console.log(x)
            // Check if the two rows should switch place:
            if (parseInt(x.innerHTML) > parseInt(y.innerHTML)) {
                // If so, mark as a switch and break the loop:
                shouldSwitch = true;
                break;
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}

sortTable("display_teams")
