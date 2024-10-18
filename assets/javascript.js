// Fetch the killfeed_data.json file
fetch('assets/killfeed_data.json')
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        // Process the data and display it
        const killfeedDiv = document.getElementById("scoreboard");

        // Loop over each player and their stats
        for (const [playerName, stats] of Object.entries(data)) {
            // Create a row for each player
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${playerName}</td>
                <td>${stats.kills}</td>
                <td>${stats.deaths}</td>
                <td>${stats.assists}</td>
                <td>${stats.kd.toFixed(2)}</td>
            `;
            // Append the row to the table body
            scoreboard.querySelector("tbody").appendChild(row);
        }

        // Append the table to the killfeedDiv
        killfeedDiv.appendChild(scoreboard);
    })
    .catch(error => console.error('Error fetching the JSON data:', error));

// Fetch the utility_damage_data.json file
fetch('assets/utility_damage_data.json')
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        // Process the data and display it
        const utilityDiv = document.getElementById("utilityDamage");

        // Loop over each player and their utility damage stats
        for (const [playerName, stats] of Object.entries(data)) {
            // Create a row for each player
            const row = document.createElement("tr");
            row.innerHTML = `
            <td>${playerName}</td>
            <td>${stats.he_damage}</td>
            <td>${stats.molotov_damage}</td>
            <td>${stats.utility_damage}</td>
        `;
            // Append the row to the table body
            utilityDamage.querySelector("tbody").appendChild(row);
        }

        // Append the table to the utilityDiv
        utilityDiv.appendChild(utilityDamage);
    })
    .catch(error => console.error('Error fetching the JSON data:', error));
