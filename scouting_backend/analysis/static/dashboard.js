document.getElementById("button").onclick = () => {
    var comp = document.getElementById("comp").value
    var match = document.getElementById("match").value
    fetch(`/analysis/api/get_match_schedule/${comp}/${match}`)
        .then(response => response.json())
        .then(data => {

            document.getElementById("red1-team").innerText = data["red1"][0]
            document.getElementById("red1-climb").innerText = data["red1"][1]
            document.getElementById("red1-tu").innerText = data["red1"][2]
            document.getElementById("red1-tl").innerText = data["red1"][3]
            document.getElementById("red1-au").innerText = data["red1"][4]
            document.getElementById("red1-al").innerText = data["red1"][5]
            document.getElementById("red1-tp").innerText = data["red1"][6]

            document.getElementById("red2-team").innerText = data["red2"][0]
            document.getElementById("red2-climb").innerText = data["red2"][1]
            document.getElementById("red2-tu").innerText = data["red2"][2]
            document.getElementById("red2-tl").innerText = data["red2"][3]
            document.getElementById("red2-au").innerText = data["red2"][4]
            document.getElementById("red2-al").innerText = data["red2"][5]
            document.getElementById("red2-tp").innerText = data["red2"][6]

            document.getElementById("red3-team").innerText = data["red3"][0]
            document.getElementById("red3-climb").innerText = data["red3"][1]
            document.getElementById("red3-tu").innerText = data["red3"][2]
            document.getElementById("red3-tl").innerText = data["red3"][3]
            document.getElementById("red3-au").innerText = data["red3"][4]
            document.getElementById("red3-al").innerText = data["red3"][5]
            document.getElementById("red3-tp").innerText = data["red3"][6]

            document.getElementById("blue1-team").innerText = data["blue1"][0]
            document.getElementById("blue1-climb").innerText = data["blue1"][1]
            document.getElementById("blue1-tu").innerText = data["blue1"][2]
            document.getElementById("blue1-tl").innerText = data["blue1"][3]
            document.getElementById("blue1-au").innerText = data["blue1"][4]
            document.getElementById("blue1-al").innerText = data["blue1"][5]
            document.getElementById("blue1-tp").innerText = data["blue1"][6]

            document.getElementById("blue2-team").innerText = data["blue2"][0]
            document.getElementById("blue2-climb").innerText = data["blue2"][1]
            document.getElementById("blue2-tu").innerText = data["blue2"][2]
            document.getElementById("blue2-tl").innerText = data["blue2"][3]
            document.getElementById("blue2-au").innerText = data["blue2"][4]
            document.getElementById("blue2-al").innerText = data["blue2"][5]
            document.getElementById("blue2-tp").innerText = data["blue2"][6]

            document.getElementById("blue3-team").innerText = data["blue3"][0]
            document.getElementById("blue3-climb").innerText = data["blue3"][1]
            document.getElementById("blue3-tu").innerText = data["blue3"][2]
            document.getElementById("blue3-tl").innerText = data["blue3"][3]
            document.getElementById("blue3-au").innerText = data["blue3"][4]
            document.getElementById("blue3-al").innerText = data["blue3"][5]
            document.getElementById("blue3-tp").innerText = data["blue3"][6]

        })

}