window.onload = function(){
    $(".table-schedule").on('click', '.row-remove', function(event) {
      $(this).parent().parent().remove();
    });

      $('#areaSelected').on('change', function() {
        // updateflag = 1 -> select area;
        $.ajax({
          type: 'POST',
          url: 'updateSchedule',
          data: {
            area: this.value,
            updateflag: 1,
          },
          success: function(data) {
            console.log(data)
            tempTag = "<option vlaue='default' selected>지점선택</option>"
            for (i = 0; i < data.length; i++) {
              tempTag = tempTag + "<option value=" + data[i]['pk'] + ">" + data[i]['fields']['bname'] + "</option>"
            }
            document.getElementById('branch').innerHTML = tempTag
          }
        });
      })

      $('#branch').on('change', function() {
        // updateflag = 1 -> select area;
        $.ajax({
          type: 'POST',
          url: 'acaUpdateSchedule',
          data: {
            branch: this.value,
            acaSelected: 1,
          },
          success: function(data) {
            console.log(data)
            tempTag = ""
            for (i = 0; i < data.length; i++) {
              tempTag = tempTag + "<option value=" + data[i]['pk'] + ">" + data[i]['fields']['name'] + "</option>"
            }
            document.getElementById('academy_branch').innerHTML = tempTag
            $('#academy_branch').selectpicker('refresh');
          }
        });
      })

      $(document).on('change','#academyselect',function() {
        $.ajax({
          type: 'POST',
          url: 'studentLoad',
          data: {
            aid: this.value,
          },
          success: function(data) {
            console.log(data)
            tempTag = ""
            for (i = 0; i < data.length; i++) {
              tempTag = tempTag + "<option value=" + data[i]['pk'] + ">" + data[i]['fields']['sname'] + "</option>"
            }
            document.getElementById('studentList').innerHTML = tempTag
            $('#studentList').selectpicker('refresh');
          }
        });
      })

      $( ".table-body" ).sortable({
         update: function( event, ui ){
           $(this).children().each(function(index) {
                $(this).find('td')
              });
            }
      });

}
