$(document).ready(function(){

  $(".collapse").on('shown.bs.collapse', function(){
    window.dispatchEvent(new Event('resize'));
  });

});
