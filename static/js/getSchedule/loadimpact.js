var loadModule = (function () {
  var loadObj;
  var presentTime;

  function setLoadObj(obj){
    loadObj = obj;
  }

  function setPresentTime(date){
    presentTime = date.getHours().toString()+":"+ (date.getMinutes()<10 ? '0' : '') + date.getMinutes().toString();
  }

  function compareLoadTime(){
      for ( var i in loadObj ){
        if (loadObj[i].innerText == presentTime){
          return loadObj[i];
        }
      }
  }
  function getPresentTime(){
    return presentTime;
  }

  function getLoadObj(){
    return loadObj;
  }

  return {
    setLoadObj : setLoadObj,
    setPresentTime : setPresentTime,
    compareLoadTime : compareLoadTime,
    getLoadObj: getLoadObj,
    getPresentTime: getPresentTime,
  };

})();
