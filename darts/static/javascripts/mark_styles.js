$(function(){

	var layers = [];
	var history = [];
	var addHistory = true;

	var canvas = this.__canvas = new fabric.Canvas("mark-style", {
		isDrawingMode: true,
		selection: false
	});

	fabric.Object.prototype.transparentCorners = false;

	var $drawingColor = $("#drawing-color");
	var $drawingLineWidth = $("#drawing-line-width");

	canvas.freeDrawingBrush = new fabric['PencilBrush'](canvas);

	$drawingColor.on("change", function(){
		canvas.freeDrawingBrush.color = this.value;
	});

	$drawingLineWidth.on("input", function() {
		canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
		$("#drawing-line-width-info").html(this.value);
	}).trigger("input");

	if (canvas.freeDrawingBrush) {
		canvas.freeDrawingBrush.color = $drawingColor.val();
		canvas.freeDrawingBrush.width = parseInt($drawingLineWidth.val(), 10) || 1;
	}

	$("#clear-canvas").on("click", function(){
		canvas.clear();
		layers = [];
		enableDrawing();
		renderLayers();
		history = [];
	});

	$("#clear-layer").on("click", function(){
		canvas.clear();
		history.push(JSON.stringify(canvas));
	});

	$(".add-layer").on("click", function() {
		var source = $(this);
		layers[source.data("layer")] = {
			png: canvas.toDataURL(),
			svg: canvas.toSVG(),
			json: JSON.stringify(canvas)
		};
		renderLayers();
	});

	function renderLayers(){
		$(".layer-preview").empty();
		var enabled = true;
		for(var i = 0; i < 3; i++){
			if(typeof layers[i] == "undefined"){
				enabled = enabled && false;
			} else {
				$(".layer-preview[data-layer=" + i + "]").html($("<img />").attr("src", layers[i]["png"]));
			}
		}
		$("#create-mark-style").prop("disabled", !enabled);
	}

	function disableDrawing(){
		canvas.isDrawingMode = false;
		canvas.deactivateAll();
		canvas.forEachObject(function(o) {
			o.selectable = false;
		});
	}

	function enableDrawing(){
		canvas.isDrawingMode = true;
	}

	$("#mark-style-form").on("submit", function(){
		var source = $(this);
		source.find("input[name=one]").val(layers[0]["svg"]);
		source.find("input[name=two]").val(layers[1]["svg"]);
		source.find("input[name=three]").val(layers[2]["svg"]);
	});

	$(".form-delete").on("submit", function(){
		return confirm("Are you sure you want to delete this mark style?");
	});


	canvas.on("object:added", function(){
		if(!addHistory) return;
		history.push(JSON.stringify(canvas));
	});

	$("#undo-btn").on("click", function(){
		addHistory = false;
		history.pop();
		if(history.length > 0){
			canvas.loadFromJSON(history[history.length - 1]);
		} else {
			canvas.clear();
		}
		canvas.renderAll();
		addHistory = true;
	});

	$(".layer-preview").on("click", function(){
		addHistory = false;
		canvas.loadFromJSON(layers[$(this).data("layer")]["json"]);
		canvas.renderAll();
		history = [];
		addHistory = true;
	});

	if(typeof markStyleId != "undefined"){
		loadMark(0);
	}

	function loadMark(mark){
		fabric.loadSVGFromString(svgs[mark], function(objects, options){
			var obj = fabric.util.groupSVGElements(objects, options);
			canvas.add(obj).centerObject(obj).renderAll();
			obj.setCoords();
			$(".add-layer[data-layer=" + mark + "]").click();
			$("#clear-layer").click();

			if(mark < svgs.length - 1){
				loadMark(mark + 1);
			}
		});
	}

});
