let entities = [];

function go() {
    for (let entity of entities) {
        map.geoObjects.remove(entity);
    }
    entities = [];

    const traf = {}, traf2 = {};

    for (const city1 in citiesGeo) {
        for (const city2 in citiesGeo) {
            traf[city1 + ':' + city2] = 0;
            traf2[city1 + ':' + city2] = 0;
        }
    }

    const interested = [];
    $('#cities').children().each((i, el) => {
        let from = $(el).find('.from :selected').text();
        let to = $(el).find('.to :selected').text();
        console.log(from, to);
        interested.push({from, to});
    });

    function isInterested(city1, city2) {
        if (interested.length) {
            let bad = true;
            for (let {from, to} of interested) {
                if ((city1 == from && city2 == to) || (city2 == from && city1 == to)) {
                    return true;
                }
            }
            return false;
        }
        return true;
    }

    let trafMx = 1;
    const dayLo = document.getElementById('day1').value;
    const dayHi = document.getElementById('day2').value;
    for (const {from, to, date, traffic} of trafficData) {
        const dayx = date.substr(0, 10);
        if (dayLo <= dayx && dayx <= dayHi && isInterested(from, to)) {
            traf[from + ':' + to] += traffic;
            traf[to + ':' + from] += traffic;

            if (traf[from + ':' + to] > trafMx) {
                trafMx = traf[from + ':' + to];
            }

            traf2[from + ':' + to] += traffic;
        }
    }

    const cities = Object.keys(citiesGeo);
    for (let i = 0; i < cities.length; ++i) {
        for (let j = i + 1; j < cities.length; ++j) {
            const city1 = cities[i];
            const city2 = cities[j];

            // if ((i + j) % 5 != 2) continue;
            if (traf[city1 + ':' + city2] == 0) continue;
            if (!isInterested(city1, city2)) continue;

            const line = new ymaps.Polyline([citiesGeo[city1], citiesGeo[city2]], {
                hintContent: `${city1} - ${city2}`,
                balloonContent: `${city1} - ${city2}: ${traf2[city1 + ':' + city2]}<br>` + 
                                `${city2} - ${city1}: ${traf2[city2 + ':' + city1]}`
            }, {
                strokeOpacity: traf[city1 + ':' + city2] / trafMx,
                strokeWidth: 5,
                strokeColor: '#ff0000',
            });

            map.geoObjects.add(line);
            entities.push(line);
        }
    }
}

(async function() {
    window.trafficData = await (await fetch('./traffic.json')).json();
    window.citiesGeo = await (await fetch('./cities_geo.json')).json();

    ymaps.ready(() => {
        window.map = new ymaps.Map("map", {
            center: [53.2966970909091, 41.944976636363634],
            zoom: 5
        }, {
            searchControlProvider: 'yandex#search'
        });

        for (const city in citiesGeo) {
            const placemark = new ymaps.Placemark(citiesGeo[city], {
                balloonContentBody: '<div style="font-size:24px;">' + city + '</div>',
                // iconCaption: city,
                iconContent: city,
            }, {
                // preset: 'islands#blueCircleDotIconWithCaption',
                preset: 'islands#blueStretchyIcon',
            });
            // placemark.options.set('iconImageSize', 300);
            map.geoObjects.add(placemark);
        }

        let dayLo = 'z', dayHi = '';
        for (const {from, to, date, traffic} of trafficData) {
            const dayx = date.substr(0, 10);
            if (dayx < dayLo) dayLo = dayx;
            if (dayx > dayHi) dayHi = dayx;
        }

        $('.date').attr('min', dayLo);
        $('.date').attr('max', dayHi);

        $('#day1').val(dayLo);
        $('#day2').val(dayHi);

        go();
    });
})();

document.getElementById('show').addEventListener('click', go);

function createCitySelection(cls) {
    let select = $('<select>').addClass(cls);
    for (let city in citiesGeo) {
        let option = $('<option>').text(city);
        select.append(option);
    }
    return select;
}

$('#addCity').click(() => {
    let select1 = createCitySelection('from');
    let select2 = createCitySelection('to');
    
    let div = $('<div class=line>');
    div.append($('<span>From: </span>'));
    div.append(select1);
    div.append($('<span> To: </span>'));
    div.append(select2);
    let removeButton = $('<input class=btn type=button value=->');
    div.append(removeButton);
    removeButton.click(() => {
        div.remove();
    });

    $('#cities').append(div);
});
