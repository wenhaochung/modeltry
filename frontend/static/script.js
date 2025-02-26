document.getElementById("predictButton").addEventListener("click", function() {
    const inputData = {
        category_anomaly: parseInt(document.getElementById("category_anomaly").value),
        Maker: document.getElementById("Maker").value,
        Model: document.getElementById("Model").value,
        Seat_num: parseInt(document.getElementById("Seat_num").value),
        Door_num: parseInt(document.getElementById("Door_num").value),
        repair_cost: parseFloat(document.getElementById("repair_cost").value),
        repair_hours: parseFloat(document.getElementById("repair_hours").value),
        repair_complexity: parseInt(document.getElementById("repair_complexity").value),
    };
    fetch('https://modeltry.zeabur.app/predict', {  // Flask 端點
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(inputData)
    })
    .then(response =>{ 
        if(!response.ok) {
            return response.text().then(text => { throw new Error(text) })
           }
          else {
           return response.json();
          }
    })
    .then(data => {
        document.getElementById("result").innerText = `預測結果：${data.prediction} (機率: ${(data.probability * 100).toFixed(1)}%)`;
    })
    .catch(error => {
        try {
            const errorObj = JSON.parse(error.message);
            document.getElementById("error").innerText = errorObj.error;
        } catch (e) {
            // 如果解析失败显示原始信息
            document.getElementById("error").innerText = error.message;
        }
    });
});