document.getElementById("button").onclick = () => {
    var comp = localStorage.getItem("comp")
    var match = document.getElementById("match").value
    fetch(`/analysis/api/2023/get_match_schedule/${comp}/${match}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("red1-team").innerText = data["red1"]["team_number"]
            document.getElementById("red1-auto-balance").innerText = `${data["red1"]["auto_balanced"][0]} : ${data["red1"]["auto_balanced"][1]}`
            document.getElementById("red1-auto-score").innerText = `${data["red1"]["auto_score"]}`
            document.getElementById("red1-teleop-cone").innerText = `${data["red1"]["teleop_cone"]}`
            document.getElementById("red1-teleop-cube").innerText = `${data["red1"]["teleop_cube"]}`
            document.getElementById("red1-total").innerText = `${data["red1"]["total_average"]}`

            document.getElementById("red2-team").innerText = data["red2"]["team_number"]
            document.getElementById("red2-auto-balance").innerText = `${data["red2"]["auto_balanced"][0]} : ${data["red2"]["auto_balanced"][1]}`
            document.getElementById("red2-auto-score").innerText = `${data["red2"]["auto_score"]}`
            document.getElementById("red2-teleop-cone").innerText = `${data["red2"]["teleop_cone"]}`
            document.getElementById("red2-teleop-cube").innerText = `${data["red2"]["teleop_cube"]}`
            document.getElementById("red2-total").innerText = `${data["red2"]["total_average"]}`

            document.getElementById("red3-team").innerText = data["red3"]["team_number"]
            document.getElementById("red3-auto-balance").innerText = `${data["red3"]["auto_balanced"][0]} : ${data["red3"]["auto_balanced"][1]}`
            document.getElementById("red3-auto-score").innerText = `${data["red3"]["auto_score"]}`
            document.getElementById("red3-teleop-cone").innerText = `${data["red3"]["teleop_cone"]}`
            document.getElementById("red3-teleop-cube").innerText = `${data["red3"]["teleop_cube"]}`
            document.getElementById("red3-total").innerText = `${data["red3"]["total_average"]}`


            document.getElementById("blue1-team").innerText = data["blue1"]["team_number"]
            document.getElementById("blue1-auto-balance").innerText = `${data["blue1"]["auto_balanced"][0]} : ${data["blue1"]["auto_balanced"][1]}`
            document.getElementById("blue1-auto-score").innerText = `${data["blue1"]["auto_score"]}`
            document.getElementById("blue1-teleop-cone").innerText = `${data["blue1"]["teleop_cone"]}`
            document.getElementById("blue1-teleop-cube").innerText = `${data["blue1"]["teleop_cube"]}`
            document.getElementById("blue1-total").innerText = `${data["blue1"]["total_average"]}`

            document.getElementById("blue2-team").innerText = data["blue2"]["team_number"]
            document.getElementById("blue2-auto-balance").innerText = `${data["blue2"]["auto_balanced"][0]} : ${data["blue2"]["auto_balanced"][1]}`
            document.getElementById("blue2-auto-score").innerText = `${data["blue2"]["auto_score"]}`
            document.getElementById("blue2-teleop-cone").innerText = `${data["blue2"]["teleop_cone"]}`
            document.getElementById("blue2-teleop-cube").innerText = `${data["blue2"]["teleop_cube"]}`
            document.getElementById("blue2-total").innerText = `${data["blue2"]["total_average"]}`

            document.getElementById("blue3-team").innerText = data["blue3"]["team_number"]
            document.getElementById("blue3-auto-balance").innerText = `${data["blue3"]["auto_balanced"][0]} : ${data["blue1"]["auto_balanced"][1]}`
            document.getElementById("blue3-auto-score").innerText = `${data["blue3"]["auto_score"]}`
            document.getElementById("blue3-teleop-cone").innerText = `${data["blue3"]["teleop_cone"]}`
            document.getElementById("blue3-teleop-cube").innerText = `${data["blue3"]["teleop_cube"]}`
            document.getElementById("blue3-total").innerText = `${data["blue3"]["total_average"]}`
        })

}