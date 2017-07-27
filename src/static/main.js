(function() {
    var coord_data;
    var last_slider_value;
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    socket.on('connect', function() {
      // socket.emit('my event', {data: 'I\'m connected!'});
    });

    var paths = [];

    socket.on('data response', function(data) {
        console.log(data);
        console.log(parseFloat(data[0][0][1][0]));
        var first = new google.maps.LatLng(parseFloat(data[0][0][1][0]),parseFloat(data[0][0][1][1]));
        var second = new google.maps.LatLng(parseFloat(data[0][1][1][0]),parseFloat(data[0][1][1][1]));
        current_bounds = map.getBounds()
        if (!current_bounds.contains(second)) {
            console.log('here');
            map.setCenter(first);
        }
        coords = [first, second];
        var flightPath = new google.maps.Polyline({
          path: coords,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 5
        });
        paths.push(flightPath);
        flightPath.setMap(map);
        $('h3').text(data[1][0]);
        if (paths.length == 1) {
          map.setCenter(first);
        }
        else if (paths.length == 5) {
          var removed = paths.shift()
          removed.setMap(null);
        }
    });

    $('#timeSelector').on('input', function() {
        value = parseInt($(this).val());
        if (Math.abs(value - last_slider_value) > 10) {
            for (var i = 0; i < paths.length; i++) {
                paths[i].setMap(null);
            }
        }
        last_slider_value = value;
        var first = new google.maps.LatLng(parseFloat(coord_data[value][1][0]),parseFloat(coord_data[value][1][1]));
        var second = new google.maps.LatLng(parseFloat(coord_data[value+1][1][0]),parseFloat(coord_data[value+1][1][1]));

        current_bounds = map.getBounds()
        if (!current_bounds.contains(second)) {
            console.log('here');
            map.setCenter(first);
        }

        coords = [first, second];
        var flightPath = new google.maps.Polyline({
          path: coords,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 5
        });
        paths.push(flightPath);
        flightPath.setMap(map);
        $('h3').text(coord_data[value][0]);
        if (paths.length == 1) {
          map.setCenter(first);
        }
        else if (paths.length == 5) {
          var removed = paths.shift()
          removed.setMap(null);
        }
    });

    socket.on('data ready', function(data) {
        // console.log(center)
        // console.log(center[0]);
        // console.log(center[1]);
        // map.setCenter(new google.maps.LatLng(center[0], center[1]));
        coord_data = data;
        console.log(coord_data);
        $('#timeSelector').attr('max', data.length-2);
        last_slider_value = 0;
    })

    $('#goButton').click(function() {
        socket.emit('start', [$('#startDateSelector').val(), $('#endDateSelector').val()])
    })
})();