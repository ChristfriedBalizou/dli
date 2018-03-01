"use strict";

var page = (function(page){

    var tables;
    var viewer;

    // EXPLORE SECTION
    var $exploreList        = $("#table-explore-list");

    // DIAGRAM
    var $imageContainer     = $(".relation-image-container");
    var $image              = $(".relation-image");
    var $diagramConainer    = $(".diagram-container");
    var $diagramContent     = $(".diagram-content");
    var $diagramCols        = $("#diagram-cols");
    var $diagramAI          = $("#diagram-ai");
    var $diagramDeleted     = $("#diagram-deleted");
    var $diagramHuman       = $("#diagram-human");
    var $imageLoaderMsg     = $(".image-loading-message");
    var $reloadGraph        = $("#reload-graph");
    var $imageDragon        = $("#image-dragon");

    // RELATION SECTION
    var $relationsLink      = $('#relations-link');
    var $relationsContent   = $('#relations-content');


    page.relation = {
        init: function() {

            $diagramCols.add($diagramAI)
                        .add($diagramHuman)
                        .add($diagramDeleted)
                        .change(function(){
                            drawGraph(tables, page.relation.buildOptions());
            });
            
            $reloadGraph.click(function(){
                drawGraph(tables, page.relation.buildOptions());
            });

            $relationsContent.empty();
            $image.empty();
            
        },

        buildOptions: function() {
            return {show_columns: $diagramCols.is(":checked"),
                    decoration: false,
                    draw_ai: $diagramAI.is(":checked"),
                    draw_human: $diagramHuman.is(":checked"),
                    draw_deleted: $diagramDeleted.is(":checked")};
        },

        render: function() {

            tables = Array.prototype
                          .slice
                          .call(arguments);

            // Set explore table list
            $exploreList.html(tables.map(tableExploreList));
            componentHandler.upgradeElement($exploreList[0]);

            // Request image
            var relLoader = loader.start({container: $relationsLink,
                element: $relationsContent});

            drawGraph(tables, page.relation.buildOptions())
                .then(function(data){
                    if(data.response.data && data.response.data.relations) {
                        relations.render(data.response.data.relations, $relationsContent[0]);
                    }
                    relLoader();
                });
        }
    };

    return page;


    function drawGraph(tables, options) {

        if(options == undefined) {
            options = {};
        }

        $imageLoaderMsg.hide();
        $imageDragon.hide();
        $image.addClass("hide");
                        
        if(viewer) {
            viewer.world.removeItem(viewer.world.getItemAt(0));
        }

        return server.getDiagram(tables, options)
            .success(function(data){
                //TODO common response handler
                if(data.status != true) {
                    console.error(data.response.message)
                    $imageLoaderMsg.show();
                    $image.addClass("hide");
                    return;
                }

                // Check if image exist before loading
                if(data.response.data.filename){
                    $image.removeClass("hide");
                    server.imageExist(data.response.data.filename)
                          .done(function(resp){
                              if(resp.status === 1) {

                                  if(resp.size.w > $diagramConainer.width()){
                                      resp.size.w = $diagramConainer.width();
                                  }

                                  $imageDragon.width(resp.size.w -10);
                                  $imageDragon.height(resp.size.h -10);

                                  if(!viewer) {
                                      viewer = OpenSeadragon({
                                          showNavigationControl: false,
                                          // defaultZoomLevel: ,
                                          id: "image-dragon",
                                          tileSources: [{
                                              type: "image",
                                              url: "/image/" + data.response.data.filename
                                          }]
                                      });
                                  } else {
                                      viewer.addTiledImage({
                                          tileSource: {
                                              type: "image",
                                              url: "/image/" + data.response.data.filename
                                          }
                                      });
                                  }
                                  $image.addClass("hide");
                                  return;
                              }
                              $image.addClass("hide");
                              $imageLoaderMsg.show();
                          });
                }
            }).always(loader.start({container: $imageContainer,
                                    element: $imageDragon}));
    }


    function tableExploreList(value) {
        return ('<span class="mdl-chip mdl-chip--contact">' +
                    '<span class="mdl-chip__contact mdl-color--indigo mdl-color-text--white">'+ 
                        '<i class="material-icons">grid_on</i>' +
                    '</span>' +
                    '<a href="/#table/'+ value +'" class="mdl-chip__text no-decoration">'+ value + '</a>' +
                    '<a href="/#table/'+ value +'" class="mdl-chip__action">' +
                        '<i class="material-icons">open_in_browser</i>' +
                    '</a>' +
                '</span>');
    }



})(page || {});
