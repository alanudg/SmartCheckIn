moment.locale('es');
var momentFlaskFront = (function(){

  /**
   * Define el offset en minuto desde el tiempo local a UTC
   * @var {number} _diff
   */
  var _diff = new Date().getTimezoneOffset()*-2;

  /**
   * Retorna una fecha dada, con una diferencia de diff minutos
   * en formato yyyy-mm-dd HH:mm:ss
   *
   * @param {String} date
   * @param {Number} [diff=0]
   * @return {Date}
   */
  var _utcToGmt = function(date, diff){
    if(!diff){
      diff = 0;
    }
    return new Date(new Date(date).getTime() + (diff * 60000)).toISOString().replace('T', ' ').replace('.000Z','');
  }

  /**
   * Obtiene todos los elementos DOM que cuenten con el atributo data-date-format
   * y corrige su contenido de manera que se pueda comunicar entre tiempo local
   * y el tiempo del servidor (asume que el tiempo del servidor será UTC)
   *
   * @param {String} date
   * @param {Number} [diff=0]
   * @return {Date}
   */
  var momentApplyDiff = function(diff){
    $('[data-date-format]').each(function(k, v){
        var _newValue = '';
        if(v.value.indexOf(' to ') != -1){
            var _dates = v.value.split(' to ');
            var _date1 = _utcToGmt(_dates[0], diff);
            var _date2 = _utcToGmt(_dates[1], diff);
            _newValue = _date1 + ' to ' + _date2;
        }else{
            _newValue = _utcToGmt(v.value, diff);
        }
        v.value = _newValue;
    });
  }

  var applyFromUtc = function(){
    momentApplyDiff();
  }

  var applyToUtc = function(){
    momentApplyDiff(_diff);
  }

  /**
   * Aplica el formato format, cuyos posibles valores son
   * ['calendar', 'fromNow', 'format'] sobre la fecha momentTime
   * y lo pone dentro del elemento _el
   * En caso de que format contenga 'format', se aplicará el formato que
   * contenga customFmt
   * @param {DOMElement} _el
   * @param {momentObject} momentTime
   * @param {String} [format='fromNow']
   * @param {String} [customFmt='']
   */
  var momentApplyCustomFmtEl = function(_el, momentTime, format, customFmt){
    if (!format) {
        format = 'fromNow';
    }
    if (!customFmt) {
        customFmt = '';
    }
    var momentHtml = "";
    switch (format) {
      case "calendar":
        momentHtml = momentTime.calendar();
        break;
      case "fromNow":
        momentHtml = momentTime.fromNow();
        break;
      case "format":
        momentHtml = momentTime.format(customFmt);
        break;
    }
    _el.html(momentHtml);
  }

  var momentApplyAbsoluteFmtEl = function(_el, momentTime){
    momentApplyCustomFmtEl(_el, momentTime, 'format', 'DD/MM/YYYY, hh:mm:ss');
  }

  var momentApplyCustomFmt = function(){
    momentApplyFmt(momentApplyCustomFmtEl);
  }

  var momentApplyAbsoluteFmt = function(){
    momentApplyFmt(momentApplyAbsoluteFmtEl);
  }

  var momentApplyFmt = function(callback){
    $("[data-date]").each(function(k, el){
        var _el = $(el);
        var format = _el.attr('data-format');
        var customFmt = _el.attr('data-customfmt')
        var momentTime = moment(new Date(_el.attr('data-date')));
        callback(_el, momentTime, format, customFmt);
        _el.attr('title', momentTime.format('dddd, MMMM Do YYYY, h:mm:ss a'));
        _el.attr('alt', momentTime.format('dddd, MMMM Do YYYY, h:mm:ss a'));
    });
  }

  return {
    applyCustomFmt : momentApplyCustomFmt,
    applyAbsoluteFmt : momentApplyAbsoluteFmt,
    applyFromUtc : applyFromUtc,
    applyToUtc : applyToUtc,
  };
})();

momentFlaskFront.applyCustomFmt();

$('#moment-absolute').click(function(){
  momentFlaskFront.applyAbsoluteFmt()
});
$('#moment-relative').click(function(){
  momentFlaskFront.applyCustomFmt()
});

momentFlaskFront.applyToUtc();

$('#filter_form button[type=submit]').click(function(){
  momentFlaskFront.applyFromUtc();
});
