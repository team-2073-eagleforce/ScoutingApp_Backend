document.getElementById("button").onclick = () => {
    var comp = document.getElementById("comp").value
    var match = document.getElementById("match").value
    fetch(`/analysis/api/get_match_schedule/${comp}/${match}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById("red1-team").innerText = data["red"][0].split("frc")[1]
        document.getElementById("red2-team").innerText = data["red"][1].split("frc")[1]
        document.getElementById("red3-team").innerText = data["red"][2].split("frc")[1]
        
        document.getElementById("blue1-team").innerText = data["blue"][0].split("frc")[1]
        document.getElementById("blue2-team").innerText = data["blue"][1].split("frc")[1]
        document.getElementById("blue3-team").innerText = data["blue"][2].split("frc")[1]

    })
    
}