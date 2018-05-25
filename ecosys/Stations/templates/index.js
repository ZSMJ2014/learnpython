//

$(function () {


    var GD_LAYER = new ol.layer.Tile({
        name: "img",
        source: new ol.source.XYZ({
            url: "https://webst0{1-4}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}"
        })
    });


    var STATIONLAYER = null;
    var BaseMap = null;

    var get_map = function () {
        if (BaseMap == null) {
            BaseMap = new ol.Map({
                    layers: [GD_LAYER],
                    target: 'map',
                    view: new ol.View({
                        center: ol.proj.transform([107.6, 35.2], 'EPSG:4326', 'EPSG:3857'),
                        zoom: 4,
                        minZoom: 2
                    })
                }
            );
        }
        return BaseMap;
    };

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                var csrftoken = $.cookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#file-upload-submit").click(function () {
        var formData = new FormData($("#datafile-form")[0]);
        $.ajax({
            type: "post",
            url: "/upload_data",
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            dataType: "json",
            success: function (data) {
                console.log(data);
                $('#table_data').empty();
                var rowArr = data.split('\n');

                var collen = rowArr[0].replace(/\s+/g, ',').split(',').length;

                var firstrow = $("<tr>")
                for (var i = 0; i < collen; i++) {
                    firstrow.append('<td>' + i + '</td>');
                }
                ;
                $("#table_data").append(firstrow);

                for (var r = 0; r < rowArr.length; r++) {
                    // {#                    连续多个空格替换为逗号#}
                    var rowdata = rowArr[r].replace(/\s+/g, ',').split(',');
                    var tr = $("<tr>")
                    for (var i = 0; i < collen; i++) {
                        tr.append('<td>' + rowdata[i] + '</td>');
                    }
                    ;
                    $("#table_data").append(tr);
                }
            },
            error: function () {
                alert('上传失败');
            }
        });
    });


    $("#params_submit").on('click', function () {
        $.ajax({
            type: 'post',
            url: "/submit_cols_num",
            data: {
                "species-col": $("#species-col").val(),
                "long-col": $("#long-col").val(),
                "lat-col": $("#lat-col").val()
            },

            success: function (sample_location) {
                var STATION_DATA = sample_location.replace(/ + /g, ',');
                var stationSource = new ol.source.Vector();
                var STATION_FEATURES = null;
                csv2geojson.csv2geojson(STATION_DATA, {
                    latfield: "c",
                    lonfield: "d",
                    delimiter: ",",
                    src_crs: "EPSG:4326",
                    dst_crs: "EPSG:3857"
                }, function (err, data) {
                    STATION_FEATURES = (new ol.format.GeoJSON()).readFeatures(data);
                    stationSource.addFeatures(STATION_FEATURES);
                });

                if (STATIONLAYER != null) {
                    get_map().removeLayer(STATIONLAYER)
                }

                STATIONLAYER = new ol.layer.Vector({
                    source: new ol.source.Cluster({
                        distance: 40,
                        source: stationSource
                    }),
                    style: function (feature) {
                        var size = feature.get('features').length;
                        return new ol.style.Style({
                            image: new ol.style.Icon({
                                src: "/static/poi.png",
                                anchor: [0.5, 1]
                            }),
                            text: new ol.style.Text({
                                text: size.toString(),
                                fill: new ol.style.Fill({
                                    color: '#fff'
                                }),
                                offsetX: 0,
                                offsetY: -15
                            })
                        });
                    }
                });
                get_map().addLayer(STATIONLAYER)

                console.log(sample_location);
            },
            error: function () {
                alert('指数计算数据所在列提交失败');
            }
        });
    });

    $("#nav-chart-tab").on('click', function () {
        $.ajax({
            type: 'get',
            url: "/show_chart",
            success: function (species_data) {
                console.log(species_data);
                $("#species_chart").empty().html('<div id="echarts_0" style="width:1500px; height:500px"> </div>');
                var myChart = echarts.init(document.getElementById('echarts_0'));
                // specify chart configuration item and data
                var option = {
                    title: {
                        text: '物种类型'
                    },
                    tooltip: {},
                    legend: {
                        data: ['数量']
                    },
                    xAxis: {
                        data: Object.keys(species_data)
                    },
                    yAxis: {},
                    series: [{
                        name: '数量',
                        type: 'bar',
                        data: Object.values(species_data),
                    }]
                };

                // use configuration item and data specified to show chart
                myChart.setOption(option);
            },
            error: function () {
                alert('物种数量分布统计失败');
            }
        });
    });




    $("#data-file").on("change", function () {
        $("#file-upload-submit").trigger("click");
    });

    $("#bioindexCompute").on('click', function (){
    // function bioindexCompute() {
        $.ajax({
            type: 'get',
            url: "/cal_bioindex",
            success: function (results) {
                console.log(results);
                var html = [ "生物多样性指数计算结果如下：<br> "  ];
                html.push( "物种丰富度 = " + results["r"] );
                html.push( "Simpson优势度指数 = " + results["s"] );
                html.push( "Shannon-Wiener多样性指数 = " + results["sw"] );
                //
                $("#results").html( html.join("<br>") );

            },
            error: function () {
                alert('生物多样性指数计算失败');
            }
        });
    });

    function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


// {#    var GD_LAYER = new ol.layer.Tile({#}
// {#        name: "img",#}
// {#        source: new ol.source.XYZ({#}
// {#            url: "https://webst0{1-4}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}"#}
// {#// url: 'http://127.0.0.1:8051/appmaptile?layer=img,cva&x={x}&y={y}&z={z}&fmt=png'#}
// {#        })#}
// {#    });#}
// {##}
// {#    var map = new ol.Map({#}
// {#        layers: [GD_LAYER, STATIONLAYER],#}
// {#        target: 'map',#}
// {#        view: new ol.View({#}
// {#            center: ol.proj.transform([107.6, 35.2], 'EPSG:4326', 'EPSG:3857'),#}
// {#            zoom: 4,#}
// {#            minZoom: 2#}
// {#        })#}
// {#    });#}


    function bioindexCompute() {
        $("#results").html("生物多样性指数计算结果如下： 物种丰富度: ; \n Simpson优势度指数： ；\n Shannon-Winner多样性指数: ;");
    }

    function csrfSafeMethod(method) {
// these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    $("#datafile-form").click(function () {

        $("#show_data").show();
        $(".show_form").show();


    });


})
;