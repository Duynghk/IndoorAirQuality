// Biến toàn cục
let lastPath = window.location.pathname;
let intervalId = null; // Biến để lưu id của setInterval
let currentDeviceId = null;
let chartInstances = {}; // Lưu trữ biểu đồ theo ID để quản lý

document.addEventListener("DOMContentLoaded", function() {
    let now = new Date();
    
    // Lấy ngày hôm nay ở định dạng YYYY-MM-DD
    let today = now.toISOString().slice(0, 10);
    
    // Định dạng thời gian mặc định: 00:00 cho start, 23:59 cho end
    let startDateTime = today + "T00:00";
    let endDateTime = today + "T23:59";
    
    // Gán giá trị mặc định cho input
    document.getElementById("start-date").value = startDateTime;
    document.getElementById("end-date").value = endDateTime;
});

function createChart(canvasId, label, data, timestamps , borderColor, stepSize) {
    // 📈 Xác định min, max của dữ liệu
    const dataMin = Math.min(...data);
    const dataMax = Math.max(...data);

    // 🛠️ Điều chỉnh khoảng Y (thêm một biên độ nhỏ)
    const padding = (dataMax - dataMin) * 0.1 || 1; // Nếu dataMin = dataMax thì thêm khoảng nhỏ
    const yMin = dataMin - padding;
    const yMax = dataMax + padding;
    let canvas = document.getElementById(canvasId);
    let ctx = canvas.getContext('2d');

    // 🔥 Nếu đã có biểu đồ trên canvas này, hủy trước khi tạo mới
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }

    // 🎨 Tạo biểu đồ mới và lưu vào chartInstances
    chartInstances[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: label,
                data: data,
                borderColor: borderColor,
                borderWidth: 2,
                fill: false,
                pointStyle: 'circle',
                pointRadius: 1,
                pointHoverRadius: 3
            }]
        },
        options: {
            scales: {
                y: {
                    min: yMin,
                    max: yMax,
                    ticks: {
                        stepSize: stepSize
                    }
                }
            }
        }
    });
}

function updateHistorySensorData(data){
    console.log(data)
    const timestamps = data.timestamps;
    const co2Data = data.co2_data;
    const temperatureDataScd4x = data.temperature_data_scd4x;
    const humidityDataScd4x = data.humidity_data_scd4x;
    
    const temperatureDataBme680 = data.temperature_data_bme680;
    const humidityDataBme680 = data.humidity_data_bme680;
    const pressureDataBme680 = data.pressure_data_bme680;
    
    const tvocDataSgp41 = data.tvoc_data_sgp41;
    const noxDataSgp41 = data.nox_data_sgp41;
    
    const visibleDataLTR = data.visible_data_ltr;
    const infraredDataLTR = data.infrared_data_ltr;
    
    const nodeTemperatureData = data.node_temperature_data;
    const nodeHumidityData = data.node_humidity_data;
    
    // const xDataKxtj3 = data.x_data_kxtj3;
    // const yDataKxtj3 = data.y_data_kxtj3;
    // const zDataKxtj3 = data.z_data_kxtj3;
    
    const batteryVoltageData = data.battery_voltage_data;
    console.log(batteryVoltageData)
    document.getElementById("charts-container").style.display = "block";
    createChart('scd4xCO2Chart', 'CO2 (ppm)', co2Data, timestamps, 'green', 50);
    createChart('scd4xTemperatureChart', 'Temperature (°C)', temperatureDataScd4x, timestamps, 'red', 1);
    createChart('scd4xHumidityChart', 'Humidity (%)', humidityDataScd4x, timestamps, 'blue', 0, 100, 10);
    
    createChart('bme680TemperatureChart', 'Temperature (°C)', temperatureDataBme680, timestamps, 'red',  1);
    createChart('bme680HumidityChart', 'Humidity (%)', humidityDataBme680, timestamps, 'blue', 10);
    createChart('bme680PressureChart', 'Pressure (Pa)', pressureDataBme680, timestamps, 'purple', 0.5);
    
    createChart('sgp41TVOCChart', 'TVOC', tvocDataSgp41, timestamps, 'blue', 50);
    createChart('sgp41NOXChart', 'NOx (ppb)', noxDataSgp41, timestamps, 'blue', 1);
    
    createChart('ltrVisibleChart', 'Visible Light (Lux)', visibleDataLTR, timestamps, 'yellow', 5);
    createChart('ltrInfraredChart', 'Infrared Light (Lux)', infraredDataLTR, timestamps,'purple', 5);
    createChart('batteryVoltageChart', 'Battery Voltage (V)', batteryVoltageData, timestamps, 'orange', 25);
    // Object.keys(nodeTemperatureData).forEach(nodeId => {
    //     createChart(`node${nodeId}TemperatureChart`, `Node ${nodeId} Temperature (°C)`, nodeTemperatureData[nodeId].data, 'red', 15, 45, 1);
    //     createChart(`node${nodeId}HumidityChart`, `Node ${nodeId} Humidity (%)`, nodeHumidityData[nodeId].data, 'blue', 0, 100, 10);
    // });        
}

// Hàm kiểm tra URL và chạy hoặc dừng fetchLiveData()
function controlLiveDataFetching() {
    if (window.location.pathname === "/live-monitoring") {
        // Chỉ chạy nếu chưa có interval (tránh chạy nhiều lần)
        if (!intervalId) {
            fetchLiveData(); // Gọi ngay khi vào trang
            intervalId = setInterval(fetchLiveData, 5000);
        }
    } else {
        clearInterval(intervalId); // Dừng cập nhật khi rời trang
        intervalId = null;
    }
}

function calculateAverage(data) {
    // Helper function to calculate mean
    function calculateMean(values) {
        return values.reduce((sum, val) => sum + val, 0) / values.length;
    }

    // Helper function to calculate standard deviation
    function calculateStandardDeviation(values, mean) {
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }

    let temperatures = [];
    let humidities = [];

    // Collect temperature and humidity values
    const sensors = [data.scd4x, data.bme680, ...data.nodes];
    sensors.forEach(sensor => {
        if (sensor.temperature !== undefined) {
            temperatures.push(sensor.temperature);
        }

        if (sensor.humidity !== undefined) {
            humidities.push(sensor.humidity);
        }
    });

    // Calculate mean and standard deviation for temperature and humidity
    const tempMean = calculateMean(temperatures);
    const tempStdDev = calculateStandardDeviation(temperatures, tempMean);

    const humidityMean = calculateMean(humidities);
    const humidityStdDev = calculateStandardDeviation(humidities, humidityMean);

    // Filter out outliers (values beyond 2 standard deviations from the mean)
    temperatures = temperatures.filter(temp => Math.abs(temp - tempMean) <= 2 * tempStdDev);
    humidities = humidities.filter(humidity => Math.abs(humidity - humidityMean) <= 2 * humidityStdDev);

    // Calculate final averages
    const averageTemperature = temperatures.length > 0 ? calculateMean(temperatures) : null;
    const averageHumidity = humidities.length > 0 ? calculateMean(humidities) : null;

    return {
        averageTemperature,
        averageHumidity,
    };
}

function calculateColor(value, max_value, type) {
    let red, green, blue;
    if (type=='nox') value += 150;
    console.log(value);
    let ratio = value / max_value;

    if (ratio <= 0.1) {
        // Xanh lam (#0000FF)
        blue = 255; 
        green = 0;
        red = 0;
    }
    else if (ratio <= 0.3) {
        // Xanh lá (#00FF00)
        blue = 0; 
        green = 255;
        red = 0;        
    }
    else if (ratio <= 0.7) {
        // Từ xanh lá (#00FF00) đến cam (#FF8000)
        red = Math.min(255, ((ratio - 0.3) / 0.3) * 255); // Tăng đỏ
        green = Math.max(128, 255 - ((ratio - 0.3) / 0.3) * 127); // Giảm xanh lá từ 255 xuống 128
        blue = 0;
    } else {
        // Từ cam (#FF8000) đến đỏ (#FF0000)
        red = 255;
        green = Math.max(0, 128 - ((ratio - 0.66) / 0.34) * 128); // Giảm xanh lá từ 128 xuống 0
        blue = 0;
    }
    
    // Chuyển màu thành mã hex
    return `#${Math.round(red).toString(16).padStart(2, '0')}${Math.round(green).toString(16).padStart(2, '0')}${Math.round(blue).toString(16).padStart(2, '0')}`;
}


function updateLiveSensorData(data) {
    const averageData = calculateAverage(data);
    document.getElementById("co2_data").textContent = data.scd4x.co2;

    // Tính và cập nhật màu cho card TVOC
    let tvocColor = calculateColor(data.sgp41.TVOC, 500,'tvoc');
    document.querySelector("#tvoc_data_sgp41").parentElement.style.color = tvocColor;
    document.getElementById("tvoc_data_sgp41").textContent = data.sgp41.TVOC;
    let noxColor = calculateColor(data.sgp41.nox, 500,'nox');
    document.querySelector("#nox_data_sgp41").parentElement.style.color = noxColor;
    document.getElementById("nox_data_sgp41").textContent = data.sgp41.nox;

    document.getElementById("average_temperature").textContent = averageData.averageTemperature.toFixed(2); // Làm tròn 2 chữ số
    document.getElementById("average_humidity").textContent = averageData.averageHumidity.toFixed(2);

    document.getElementById("visible_data_ltr").textContent = data.ltr.visible_plus_ir;
    document.getElementById("infrared_data_ltr").textContent = data.ltr.infrared;

    document.getElementById("battery_voltage_data").textContent = data.battery_voltage;
    document.getElementById("power_status_data").textContent = data.power_status ? "ON" : "OFF";

    document.getElementById("temperature_data_scd4x").textContent = data.scd4x.temperature.toFixed(2); // Làm tròn 2 chữ số
    document.getElementById("humidity_data_scd4x").textContent = data.scd4x.humidity.toFixed(2);

    document.getElementById("temperature_data_bme680").textContent = data.bme680.temperature.toFixed(2);
    document.getElementById("humidity_data_bme680").textContent = data.bme680.humidity.toFixed(2);
    document.getElementById("pressure_data_bme680").textContent = data.bme680.pressure.toFixed(2);
    // Lấy thẻ cha để chứa các node
    let container = document.getElementById("node_data_container");
    container.innerHTML = ""; // Xóa nội dung cũ để cập nhật mới
    // Duyệt qua danh sách node và tạo sensor-card cho từng node
    if (data.nodes && data.nodes.length > 0) {
        console.log("Processing nodes...");
    
        // Tạo một object để lưu tổng giá trị và số lần xuất hiện của từng node_id
        let nodeMap = {};
    
        data.nodes.forEach(node => {
            if (!nodeMap[node.node_id]) {
                nodeMap[node.node_id] = { 
                    totalTemperature: 0, 
                    totalHumidity: 0, 
                    count: 0 
                };
            }
    
            nodeMap[node.node_id].totalTemperature += node.temperature;
            nodeMap[node.node_id].totalHumidity += node.humidity;
            nodeMap[node.node_id].count += 1;
        });
    
        // Xóa nội dung cũ để tránh bị lặp lại khi cập nhật dữ liệu
        let container = document.getElementById("node_data_container");
        container.innerHTML = "";
    
        // Duyệt qua danh sách node đã xử lý và hiển thị dữ liệu trung bình
        Object.keys(nodeMap).forEach(node_id => {
            let avgTemperature = (nodeMap[node_id].totalTemperature / nodeMap[node_id].count).toFixed(2);
            let avgHumidity = (nodeMap[node_id].totalHumidity / nodeMap[node_id].count).toFixed(2);
    
            let card = document.createElement("div");
            card.className = "sensor-card";
            card.innerHTML = `
                <label>Node ${node_id}:</label>
                <p><strong>Temperature:</strong> ${avgTemperature}°C</p>
                <p><strong>Humidity:</strong> ${avgHumidity}%</p>
            `;
            container.appendChild(card);
        });
    }
}

// Hàm lấy dữ liệu từ server
function fetchLiveMonitoringData(currentDeviceId) {
    fetch(`/api/live-monitoring-data?device_id=${currentDeviceId}`)
        .then(response => response.json())
        .then(data => {
            if (data) {
                console.log(data)
                updateLiveSensorData(data);  // Gọi hàm cập nhật UI
            } else {
                document.getElementById("monitoring-data").innerText = "No data available";
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Hàm kiểm tra URL và chạy hoặc dừng fetchData()
function controlLiveDataFetching() {
    if (window.location.pathname === "/live-monitoring") {
        // Chỉ chạy nếu chưa có interval (tránh chạy nhiều lần)
        if (!intervalId) {
            fetchLiveMonitoringData(currentDeviceId); // Gọi ngay khi vào trang
            intervalId = setInterval(() => fetchLiveMonitoringData(currentDeviceId), 5000);
            console.log("Fetching data started.");
        }
    } else {
        clearInterval(intervalId); // Dừng cập nhật khi rời trang
        intervalId = null;
        console.log("Fetching data stopped.");
    }
}

// Hàm chạy khi tải trang
document.addEventListener("DOMContentLoaded", () => {
    controlLiveDataFetching();
});


setInterval(() => {
    if (window.location.pathname !== lastPath) {
        lastPath = window.location.pathname;

        // Kiểm tra nếu đang ở trang /live-monitoring thì mới gọi controlLiveDataFetching
        if (window.location.pathname === "/live-monitoring") {
            controlLiveDataFetching(); // Kiểm tra và cập nhật dữ liệu
        } else {
            clearInterval(intervalId); // Dừng việc cập nhật nếu không phải /live-monitoring
            intervalId = null; // Xóa interval khi không ở trang live-monitoring
        }
    }
}, 1000);

function UpdateDeviceId() {
    const form = document.getElementById("update_live_data-form"); 
    // Add event listener to the form's submit event
    form.addEventListener("submit", onSubmit); 
    function onSubmit(event) {
      event.preventDefault();
      form.removeEventListener("submit", onSubmit);
      
      currentDeviceId = document.getElementById("device-name").value;
    }
  }