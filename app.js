
plot_element = ['plot1', 'plot2', 'plot3', 'plot4'];
plot_title = ['title1', 'title2', 'title3', 'title4'];
plot_name = ['Port1', 'Port2', 'Port3', 'Port4'];


var ws = new WebSocket('ws://localhost:8000');

var x = 1;

var plot_key = {}

ws.addEventListener('open', function (event) {
	console.log('Connected to the WS Server!')
});

// Connection closed
ws.addEventListener('close', function (event) {
	console.log('Disconnected from the WS Server!')
});




ws.onopen = function () {
	setupPlot();
	console.log('Sending mesg to server')
	ws.send("Message from client");
};


ws.onmessage = function (event) {


	//values_str = (event.data).split(',');
	data = JSON.parse(event.data)

	


	for (var key of Object.keys(data)) {
		var  info = data[key]['info']
		update_plot_key(key);
		plot_name = plot_key[key]['plot'];
		title_name = plot_key[key]['title'];
		if (info['protocol'] == 'UDP'){
			pps_val = data[key]['data']['pps'];
			jit_val = data[key]['data']['jitter'];
			media = data[key]['data']['media'];
			state = data[key]['data']['state'];
			loss_val = data[key]['data']['loss'];
			len_val =  data[key]['data']['len'];
			mbps_val = data[key]['data']['mbps']
			document.getElementById(title_name).innerHTML = `Source: ${info['srcip']}:${info['srcport']}, Destination: ${info['dstip']}:${info['dstport']}, ${info['protocol']} ,${media}: ${state} `;
			Plotly.extendTraces(plot_name, {x: [[x], [x], [x], [x]], y: [[pps_val], [mbps_val], [loss_val], [jit_val]]}, [0, 1, 2,3], 100);
		}

		if (info['protocol'] == 'TCP') {
			pps_val = data[key]['data']['pps'];
			document.getElementById(title_name).innerHTML = `Source: ${info['srcip']}:${info['srcport']}, Destination: ${info['dstip']}:${info['dstport']}, ${info['protocol']} ,${media} `;
			Plotly.extendTraces(plot_name, {x: [[x]], y: [[pps_val]]}, [0], 100);

		}

		}
		
	x++;
}


function update_plot_key(key){
	if (!(key in plot_key)){
		plot_key[key] = {
			'plot': plot_element[key],
			'title': plot_title[key],
		}
	}
	//console.log(plot_key);

}

function setupPlot(){
	
	for (var i = 0; i < 4; i++) {
		var layout = {
			title: plot_name[i],
			font: {
				family: 'Courier New, monospace',
				size: 24
			  },
			showlegend: true,
			//grid: {rows: 2, columns: 2, pattern: 'independent'},

		};

		var trace1 = {
			x: [0],
			y: [0],
			name: 'Packets per second',
		}

		var trace2 = {
			x: [0],
			y: [0],
			name: 'Mbps',
		}

		var trace3 = {
			x: [0],
			y: [0],
			name: 'Packet loss',
		}
		var trace4 = {
			x: [0],
			y: [0],
			name: 'Jitter',
		}

		var data = [trace1, trace2, trace3, trace4]
		Plotly.newPlot(plot_element[i], data, layout);

	}
};
 
