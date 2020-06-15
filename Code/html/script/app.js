const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const js2 = document.querySelector('.js-2');
const js3 = document.querySelector('.js-3');
const js4 = document.querySelector('.js-4');

// #region socket
const listenToSocket = function () {
  socket.on("connected", function () {
    console.log("verbonden met socket webserver");
  });
  socket.on("B2F_actuator_status", function (jsonObject) {
    console.log(jsonObject)
    let actuators = [`LDR`,`SOIL`,`TEMP`]
    for(i=0; i<Object.keys(jsonObject[0]).length; i++){

      const htmlactuator = document.querySelector(`.js-actuator-status[data-sensor="${Object.keys(jsonObject[0])[i]}"]`);
      if (htmlactuator) {
        let html = ``
        let color = ``
        if (Object.values(jsonObject[1])[i] == 1){
          color = `c-button--alpha-sensor`
        }else if  (Object.values(jsonObject[1])[i] == 0){
          color = `c-button--alpha-sensor-gray`
        }
        if (Object.values(jsonObject[0])[i] == 1) {
          html += `<p>${Object.keys(jsonObject[0])[i]} on</p>`;
          html += `<div class="o-layout__item u-1-of-2-bp2 c-sensor-button">
                                    <a href="#!" class="js-manual-actuator c-button-sensor ${color} c-button--md-sensor" data-sensorid="${actuators[i]}" data-status="0">turn off</a>
                                  </div>`
        }
        else if (Object.values(jsonObject[0])[i] == 0) {
          html += `<p>${Object.keys(jsonObject[0])[i]} off</p>`;
          html += `<div class="o-layout__item u-1-of-2-bp2 c-sensor-button">
                                    <a href="#!" class="js-manual-actuator c-button-sensor ${color} c-button--md-sensor" data-sensorid="${actuators[i]}" data-status="1">turn on</a>
                                  </div>`
        }
        htmlactuator.innerHTML = html
        listenToManualButtons(Object.values(jsonObject[1]));
      }
    }
  });
  socket.on("B2F_sensor_data", function (jsonObject) {
    for(i=0; i<Object.keys(jsonObject).length; i++){
      const htmlsensor = document.querySelector(`.js-sensordata[data-sensor="${Object.keys(jsonObject)[i]}"]`);
      if (htmlsensor) {
        if (Object.keys(jsonObject)[i] == "Temperature") {
          htmlsensor.innerHTML = `<div class="c-progress">
                                    <div class="c-progress-${((Object.keys(jsonObject)[i]).split(" "))[0]} c-progress-center" style="width:${Object.values(jsonObject)[i]*2}%">
                                    <p class="c-progress-text rotate-90">${Math.round(Object.values(jsonObject)[i])}°C</p>
                                    </div> 
                                  </div>`;
        }
        else{
          htmlsensor.innerHTML = `<div class="c-progress">
                                    <div class="c-progress-${((Object.keys(jsonObject)[i]).split(" "))[0]} c-progress-center" style="width:${Object.values(jsonObject)[i]/10.23}%">
                                    <p class="c-progress-text rotate-90">${Math.round(Object.values(jsonObject)[i]/10.23)}%</p>
                                    </div> 
                                  </div>`;
        }
      }
    }
  });
};
// #endregion

// #region settings
const showSettings = function(jsonObject){
  sensorsettings = jsonObject[0]
  ID1 = sensorsettings[1][0]
  ID2 = sensorsettings[2][0]
  ID3 = sensorsettings[3][0]

  U1 = sensorsettings[1][1]
  U2 = sensorsettings[2][1]
  U3 = sensorsettings[3][1]

  L1 = sensorsettings[1][2]
  L2 = sensorsettings[2][2]
  L3 = sensorsettings[3][2]

  A1 = sensorsettings[1][3]
  A2 = sensorsettings[2][3]
  A3 = sensorsettings[3][3]
  ActiveList = [A1,A2,A3]
  statuslist = [``,``,``]
  disabledlist = [``,``,``]
  for(let item in ActiveList){
    if(ActiveList[item] == 1){
      statuslist[item] = `checked`
      disabledlist[item] = ``
    }else if(ActiveList[item] == 0){
      statuslist[item] = ``
      disabledlist[item] = `disabled`
    }
  }

  datasettings = jsonObject[1]
  Name1 = datasettings[1][0]
  Name2 = datasettings[2][0]
  Name3 = datasettings[3][0]

  SP1 = datasettings[1][1]
  SP2 = datasettings[2][1]
  SP3 = datasettings[3][1] 

  startTime = jsonObject[2][0].substr(0,5)
  if (jsonObject[2][0].substr(0,1)<10){
    startTime = `0`+startTime
    startTime = startTime.substr(0,5)
  }

  stopTime = jsonObject[2][1].substr(0,5)

  const js2 = document.querySelector('.js-2');
  const js3 = document.querySelector('.js-3');
  const js4 = document.querySelector('.js-4');
  js2.innerHTML = `<div class="js-L2 u-max-width-sm o-layout__item u-1-of-3-bp3">
                    <div class="js-settings c-card__settings"> 
                      <h4 class="c-centered">Light sensor and led's</h4>
                      <p>LED's</p>
                        <label class="switch">
                          <input type="checkbox" ${statuslist[ID1-1]}>
                          <span class="slider round js-sensor-switch" data-sensorID="${ID1}"></span>
                        </label><br><br>
                      <p class="c-inline">Lower limit: </p><input class="js-sensor${ID1}-L c-input-number" type="number" name="Lower" value="${Math.round(L1/10.23)}" ${disabledlist[ID1-1]}>%<br>
                      <p class="c-inline">Upper limit: </p><input class="js-sensor${ID1}-U c-input-number" type="number" name="Upper" value="${Math.round(U1/10.23)}" ${disabledlist[ID1-1]}>%<br><br>
                    </div>
                 </div>

                 <div class="js-M2 u-max-width-sm o-layout__item u-1-of-3-bp3">
                    <div class="js-settings c-card__settings"> 
                      <h4 class="c-centered">Soil Moisture Settings and Pump</h4>
                      <p>Pump</p>
                      <label class="switch">
                          <input type="checkbox" ${statuslist[ID2-1]}>
                          <span class="slider round js-sensor-switch" data-sensorID="${ID2}"></span>
                        </label><br><br>

                      <p class="c-inline">Lower limit: </p><input class="js-sensor${ID2}-L c-input-number" type="number" name="Lower" value="${Math.round(L2/10.23)}" ${disabledlist[ID2-1]}>%<br>
                      <p class="c-inline">Upper limit: </p><input class="js-sensor${ID2}-U c-input-number" type="number" name="Upper" value="${Math.round(U2/10.23)}" ${disabledlist[ID2-1]}>%<br><br>
                    </div>
                 </div>

                 <div class="js-R2 u-max-width-sm o-layout__item u-1-of-3-bp3">
                    <div class="o-layout__item u-1-of-3-bp2">
                      <div class="js-settings c-card__settings"> 
                          <h4 class="c-centered">Temperature and heater</h4>
                          <p>Heater</p>
                          <label class="switch" >
                            <input type="checkbox" ${statuslist[ID3-1]}>
                            <span class="slider round js-sensor-switch" data-sensorID="${ID3}"></span>
                          </label><br><br>
                          <p class="c-inline">Lower limit: </p><input class="js-sensor${ID3}-L c-input-number" type="number" name="Lower" value="${L3}" ${disabledlist[ID3-1]}>°C<br>
                          <p class="c-inline">Upper limit: </p><input class="js-sensor${ID3}-U c-input-number" type="number" name="Upper" value="${U3}" ${disabledlist[ID3-1]}>°C<br><br>
                      </div>
                    </div>
                 </div>`
  
  js3.innerHTML = `<div class="js-L2 u-max-width-lg o-layout__item">
                      <div class="js-datasettings c-card__polling-settings"> 
                        <h4 class="c-centered">Other settings</h4>
                        <div class="c-evenly">

                          <div class="o-layout__item u-1-of-2-bp2">
                            <div class="c-datasettings">
                              <p>Time Limit for LED and Camera</p>
                              <p class="c-inline">from <input class="js-time-limit c-input-number-lg" type="time" name="start" value="${startTime}"></p>
                              <p class="c-inline">to <input class="js-time-limit c-input-number-lg" type="time" name="stop" value="${stopTime}"></p>
                            </div>

                            <div class="c-datasettings">
                              <p>Sensor Polling Speed</p>
                              <p class="c-inline">speed in seconds: </p><input class="js-sensor-polling c-input-number" step=".1" type="number" name="${Name1}" value="${SP1}"><br>
                            </div>
                          </div>
                          <div class="o-layout__item u-1-of-2-bp2">
                            <div class="c-datasettings">
                              <p>Database Write Speed</p>
                              <p class="c-inline">speed in minutes: </p><input class="js-sensor-polling c-input-number" step="1" type="number" name="${Name2}" value="${SP2/60}"><br>
                            </div>

                            <div class="c-datasettings">
                              <p>Picture interval</p>
                              <p class="c-inline">speed in minutes: </p><input class="js-sensor-polling c-input-number" step="1" type="number" name="${Name3}" value="${SP3/60}"><br>
                            </div>
                          </div>
                        </div>
                      </div>
                  </div>`      

  js4.innerHTML = `<div class="js-R2 u-max-width-sm o-layout__item u-1-of-3-bp3">
                    <div class="o-layout__item u-1-of-3-bp2 c-apply-button">
                    <a href="#!" class="js-ChangeSettings c-button c-button--alpha c-button--md" >Apply Settings</a>
                    </div>
                 </div>`
  
  listenToChangeSettings(sensorsettings[1][3],sensorsettings[2][3],sensorsettings[3][3]);
};

// #endregion



// #region pictures
const showPictures = function(jsonObject){
  pictures = jsonObject['data']
  Picturecount = pictures.length
  const js2 = document.querySelector('.js-2');
  const js3 = document.querySelector('.js-3');
  const js4 = document.querySelector('.js-4');
  js3.innerHTML = ``
  js4.innerHTML = ``
  js2html = `<div class="slideshow-container c-card__slideshow">`
  for(let picture in pictures){
    id = pictures[picture]['idPictures']
    date = pictures[picture]['DateTime']
    date = date.substr(0,22)
    imageLocation = pictures[picture]['imageLocation']
    imageLocation = imageLocation.split("html/")[1];
    if((Number(picture)+1) == 1){
      display= 'style="display:block;"'
    }else{
      display = 'style="display:none;"'
    }
    picturehtml = `<div class="mySlides fade" ${display}>
                      <div class="numbertext">${Number(picture)+1} / ${Picturecount}</div>
                      <img src="${imageLocation}" style="width:100%">
                      <div class="text">${date}</div>
                    </div>`
    js2html += picturehtml
  }
  js2html += `<!-- Next and previous buttons -->
                <a class="prev js-prev" href="#!">&#10094;</a>
                <a class="next js-next" href="#!">&#10095;</a>
              </div>`
  js2.innerHTML = js2html
  listenToSlideshow();
}
const listenToSlideshow = function(){
  const prev = document.querySelector(".js-prev");
  const next = document.querySelector(".js-next");
  let slideIndex = 1;
  
  // Next/previous controls
  const plusSlides = function(n) {
    showSlides(slideIndex += n);
  }
  // Thumbnail image controls
  const currentSlide = function(n) {
    showSlides(slideIndex = n);
  }
  
  const showSlides = function(n) {
    let i;
    let slides = document.querySelectorAll(".mySlides");
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex-1].style.display = "block";
  }

  prev.addEventListener("click", function(){
      plusSlides(-1);
    });

  next.addEventListener("click", function(){
      plusSlides(1);
    });
  showSlides(slideIndex);
}

// #endregion

//#region ***  GET  ***
const getPictureLocations = function(){
  handleData(`http://${lanIP}/api/v1/pictures`, showPictures);
};
const get_settings = function(){
  handleData(`http://${lanIP}/api/v1/settings`, showSettings);
}
//#endregion

// #region eventlisteners
const listenToMenu = function(){
  const menubuttons = document.querySelectorAll(`.js-menu`);
  const js2 = document.querySelector('.js-2');
  const js3 = document.querySelector('.js-3');
  const js4 = document.querySelector('.js-4');
  for(const item of menubuttons){
    item.addEventListener("click", function(){

      if (item.getAttribute("data-value") == "graphs"){
        js2.innerHTML = ` <div class="js-L2 u-max-width-sm o-layout__item u-1-of-4-bp3">
                              <div class=" c-card__settings">
                                  <p>Show sensordata of last:</p>
                                  <label class="control control-radio">
                                      day<input class="js-radio1" type="radio" name="radio" checked="checked" value="1">
                                      <div class="control_indicator">
                                      </div>
                                  </label>
                                      <label class="control control-radio">
                                          week<input class="js-radio1" type="radio" name="radio" value="7">
                                          <div class="control_indicator">
                                          </div>
                                  </label>
                              </div>
                            
                          </div>
                          <div class="js-R2 o-layout__item u-3-of-4-bp3 c-card__settings_graph">
                              <div class="js-graph">
                                  <embed type="image/svg+xml" src="img/svg/graphDayALL.svg" />
                              </div>
                          </div>`
        js3.innerHTML = ``
        js4.innerHTML = ``
      } else if (item.getAttribute("data-value") == "settings"){
        get_settings();
        
      } else if (item.getAttribute("data-value") == "pictures"){
        getPictureLocations();
      } else if ((item.getAttribute("data-value") == "shutdown")){
        console.log('shutdown')
        socket.emit("F2B_ShutDown", 'test');
      }
      listenToUI();
    })
  }
}
const listenToUI = function(){
  const radioButtons = document.querySelectorAll(`.js-radio1`);
  

  for(const radio of radioButtons){
    radio.addEventListener("click", function(){
      if (radio.value==1){
        filename = `img/svg/graphDayALL.svg`
      } else if (radio.value==7){
        filename = `img/svg/graphWeekALL.svg`
      }
      console.log(filename)
      const htmlGraph = document.querySelector(`.js-graph`);
      if (htmlGraph) {
        htmlGraph.innerHTML = `<embed type="image/svg+xml" src="${filename}"/>`;     
    }
    })
  }
}

const listenToManualButtons = function(activelist){
  
  let actuatorbuttons = document.querySelectorAll('.js-manual-actuator')
  for(let i in actuatorbuttons){
    if (activelist[i] == 1){
      actuatorbuttons[i].addEventListener("click", function(){
        sensor = actuatorbuttons[i].getAttribute('data-sensorid')
        status = actuatorbuttons[i].getAttribute('data-status')
        console.log(sensor,status)
        handleData(`http://${lanIP}/api/v1/actuators/${sensor}/${status}`, callback, callback, 'POST');
      })
    }
  }
}
const callback = function(){
  console.log('post successfull')
}


const listenToChangeSettings = function(A1,A2,A3){
  const ChangeSettings = document.querySelector('.js-ChangeSettings')
  ActiveList = [A1,A2,A3]
  ActiveToggleButtons =  document.querySelectorAll(`.js-sensor-switch`);
  for(let toggle of ActiveToggleButtons){
    toggle.addEventListener("click", function(){
      id = toggle.getAttribute("data-sensorID")-1
      ActiveList[id] = !ActiveList[id]
      inputL = document.querySelector(`.js-sensor${id+1}-L`)
      inputR = document.querySelector(`.js-sensor${id+1}-U`)
      if(ActiveList[id] == false){
        inputL.disabled = true
        inputR.disabled = true
      }else if(ActiveList[id] == true){
        inputL.disabled = false
        inputR.disabled = false
      }
    })
  }

  ChangeSettings.addEventListener("click", function(){
    ID1 = 1
    ID2 = 2
    ID3 = 3
    IDS = [ID1,ID2,ID3]
    L1 = Math.round(document.querySelector('.js-sensor1-L').value*10.23)
    L2 = Math.round(document.querySelector('.js-sensor2-L').value*10.23)
    L3 = document.querySelector('.js-sensor3-L').value
    LS = [L1,L2,L3]
    U1 = Math.round(document.querySelector('.js-sensor1-U').value*10.23)
    U2 = Math.round(document.querySelector('.js-sensor2-U').value*10.23)
    U3 = document.querySelector('.js-sensor3-U').value
    US = [U1,U2,U3]

    A1 = ActiveList[0]
    A2 = ActiveList[1]
    A3 = ActiveList[2]

    SP1 = parseFloat(document.querySelector('.js-sensor-polling[name="SensorPolling"]').value)
    SP2 = parseFloat((document.querySelector('.js-sensor-polling[name="dbWrite"]').value)*60)
    SP3 = parseFloat((document.querySelector('.js-sensor-polling[name="CameraInterval"]').value)*60)
    SPvalues = [SP1, SP2, SP3]
    Name1 = 'SensorPolling'
    Name2 = 'dbWrite'
    Name3 = 'CameraInterval'
    SPnames = [Name1,Name2,Name3]

    startTime = document.querySelector('.js-time-limit[name="start"]').value
    stopTime = document.querySelector('.js-time-limit[name="stop"]').value

    var data1 = new Object()
    for(i=0; i<3; i++){
        data1[i] = [IDS[i],US[i],LS[i],ActiveList[i]]
    }
    socket.emit("F2B_ChangeSensorSettings", data1);

    var data2 = new Object()
    for(i=0; i<3; i++){
      data2[i] = [SPnames[i],SPvalues[i]]
    }
    socket.emit("F2B_ChangeDataSettings", data2);
    
    var data3 = new Object()
    data3[0] = ['startTime',startTime]
    data3[1] = ['stopTime',stopTime]
    socket.emit("F2B_ChangeTimeSettings", data3);
  })

  
}
// #endregion 

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  
  getPictureLocations();
  socket.removeAllListeners();
  listenToSocket();
  listenToMenu();
  listenToUI();
});

