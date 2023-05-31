var vacancies = null;
google.charts.load('current', {'packages':['annotatedtimeline']});

$(document).on('click', 'a', function(e) {
  var target = $(this).attr('href');
  $('html, body').animate({scrollTop: $(target).offset().top}, 800);
  return false;
});
$(document).on('keyup', '.rq-input', function(e) {
  var id = $(this).attr('id');
  var key = this.value.toLowerCase();;
  if(key in vacancies[id][2]) {
    $(this).parent().find('.rq-result').html(((vacancies[id][2][key]/vacancies[id][1])*100).toFixed(1) + '%');
  }
  else {
    $(this).parent().find('.rq-result').html('0%');
  }
});

function encode_utf8(s) {
  return unescape(encodeURIComponent(s));
}

function decode_utf8(s) {
  return decodeURIComponent(escape(s));
}

function submit(event) {
  const keyName = event.key;
  if(keyName != "Enter") return false;
  var query = $("#q").val();
  $(".vacancies").html("<img alt='loading' width='8%' height='auto' style='margin: 10px auto;' src='/static/load.gif'/>");
  var parameters = {
        q: query
  };
  $.getJSON(Flask.url_for("vacancy"), parameters)
  .done(function(data, textStatus, jqXHR) {

    console.log('data = ' + data.length);
    console.log(data);
    $(".vacancies").empty();

    if(data.length < 2) {
      vacancies = null;
      $(".vacancies").html('<div> Вакансии не найдены </div>');
    } else {
      vacancies = [data[0], data[1][0]];
      for (var i = 1; i < data.length; i++) {
        json = JSON.parse(data[i][3]);
        vacancies.push([data[i][1], data[i][2], json, top5(json), data[i][4]]);
        draw();
        var target = $("#s");
      }
      return false;
    }
  })
  .fail(function(jqXHR, textStatus, errorThrown) {
    vacancies = null;
  });
  return false;
}

function draw() {
  if(vacancies == null) return false;
  html = '<div class="data" id="s">Данные '+vacancies[1]+'<br/>Распознано '+vacancies[0]+' вакансий</div>';
  html += '<div class="data">';
  for (var i = 2; i < vacancies.length; i++) {
    html += '<a href="#v'+(i-1)+'">['+vacancies[i][0]+']</a> ';
  }
  html += '</div>';
  for (var i = 2; i < vacancies.length; i++) {
    html += '<div class="vacancy" id="v'+(i-1)+'"><div class="head"><div class="name">' + vacancies[i][0] + '</div><div class="count">' + vacancies[i][1] + ' из ' + vacancies[0] + '</div></div>';
    if(vacancies[i][3].length == 0){
      html += '<div class="body"></div></div>';
      continue;
    }
    html += '<div class="rq-result percent"></div>';
    html += '<input id="'+i+'" class="rq-input"/><div class="hint">Введите ключевое слово</div>';
    html += '<div class="body">';
    html += '<div class="subtitle">Часто встречаются в требованиях:</div>';
    for (var key in vacancies[i][3]) {
      var len = vacancies[i][1];
      html += '<div class="require">' + vacancies[i][3][key][0] + '<div class="percent">' + ((len==0)?'0.1':((vacancies[i][3][key][1] / len) * 100).toFixed(1)) +'%' + '</div></div>';
    }
    html += '<div class="subtitle">График изменения кол-ва вакансий:</div><div class="chart" id="c'+i+'"></div></div></div>';
  }
  $(".vacancies").html(html);
  chart();
  return true;
}

function top5(json){
  var dict = json;

  var items = Object.keys(dict).map(function(key) {
      return [key, dict[key]];
  });

  items.sort(function(first, second) {
      return second[1] - first[1];
  });
  return items.slice(0, 10);
}

function chart(){
  // return "";
  for (var i = 2; i < vacancies.length; i++) {
      var data = new google.visualization.DataTable();
      data.addColumn('date', 'Дата');
      data.addColumn('number', 'Количество доступных вакансий');
      console.log(vacancies[i][4]);
      for(j in vacancies[i][4]) {
      var dt = Date.parse('1997-07-16T19:20:15');
      data.addRow([new Date(vacancies[i][4][j][0]), vacancies[i][4][j][1]]);
      }
      var chart = new google.visualization.AnnotatedTimeLine(document.getElementById('c'+i));
      chart.draw(data, {
      displayAnnotations: false,
      displayZoomButtons: false
      });
  }

}

function dateFromUTC( dateAsString, ymdDelimiter) {
    var pattern = new RegExp( "(\\d{4})" + ymdDelimiter + "(\\d{2})" + ymdDelimiter + "(\\d{2}) (\\d{2}):(\\d{2}):(\\d{2})" );
    var parts = dateAsString.match( pattern );
    return new Date( Date.UTC(
      parseInt( parts[1] )
    , parseInt( parts[2], 10 ) - 1
    , parseInt( parts[3], 10 )
    , parseInt( parts[4], 10 )
    , parseInt( parts[5], 10 )
    , parseInt( parts[6], 10 )
    , 0
    ));
}
