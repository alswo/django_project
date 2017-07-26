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

      $('#academyselect').on('change', function() {
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

      var thisObject;
      var thisObjectForAca;

      $(document).on('click', '.addstudent', function() {
        //thisObject -> studentName, thisObjectForAca -> AcademyID
        a = $(this)
        thisObject = $(this).parent().prevAll('.inputTd').children();
        thisObjectForAca = $(this).parent().nextAll('.inputAcaU').children();
        thisObjectForSid = $(this).parent().nextAll('.inputSid').children();
        console.log(thisObjectForAca);
        $('#addstu').modal('show');
      })

      $(document).on('click', '.studenttoinput', function() {
        var selectedAca = []
        var selectedStu = []
        selectedSid = $('#studentList').val()

        var aca = $('#academyselect').val()

        for (var i = 0; i < selectedSid.length; i++) {
           var val = selectedSid[i];
           var txt = $("#studentList option[value='"+val+"']").text();
            selectedStu.push(txt)
            selectedAca.push(aca)
        }

        console.log(selectedAca)

        if (thisObject[0].nodeName == 'DIV') {
          temp = thisObject[1].value
          tempAca = thisObjectForAca[0].value
          tempSid = thisObjectForSid[0].value

          if (temp != '') {
            console.log('1')
            temp += ',' + selectedStu
            tempAca += ',' + selectedAca
            tempSid += ',' + selectedSid

            $(thisObject[1]).tagsinput('add')
            //$(thisObjectForAca[0]).tagsinput('add')
            //$(thisObjectForSid[0]).tagsinput('add')

          } else {
            console.log('2')
            temp = ''+selectedStu
            tempAca = ''+selectedAca
            tempSid = ''+ selectedSid
            $(thisObject[1]).tagsinput('add')
            //$(thisObjectForAca[0]).tagsinput('add')
            //$(thisObjectForSid[0]).tagsinput('add')
          }

          $(thisObject[1]).tagsinput('add', temp)
          $(thisObjectForAca[0]).val(tempAca)
          $(thisObjectForSid[0]).val(tempSid)

        } else if (thisObject[0].nodeName == 'INPUT') {
          temp = thisObject[0].value

          if (temp != '') {
            temp += ',' + selectedStu
            tempAca += ',' + selectedAca
            tempSid += ',' + selectedSid
          } else {
            console.log('2')
            temp = ''+selectedStu
            tempAca = ''+selectedAca
            tempSid = ''+ selectedSid
            $(thisObject[0]).tagsinput('add')
          }
          $(thisObject[0]).tagsinput('add', temp)
          $(thisObjectForAca[0]).val(tempAca)
          $(thisObjectForSid[0]).val(tempSid)
        }
      })

      $(document).on('beforeItemRemove', '.inputTd', function(event) {
        t = $(this)
        sibling_sid = $(this)[0].parentNode.children[6].children[0]
        sibling_aca = $(this)[0].parentNode.children[5].children[0]

        // Do some processing here
        console.log(sibling_sid)
        console.log(sibling_aca)
        var before_list = t[0].children[1].value.split(",").map(function(item) {
          return item.trim();
        });

        var delete_index = before_list.indexOf(event.item.trim())

        var before_sid_value = sibling_sid.value
        var before_aca_value = sibling_aca.value
        console.log(before_sid_value)
        console.log(before_aca_value)

        var delete_sid = before_sid_value.split(',').map(function(item) {
          return item.trim()
        });
        var delete_aca = before_aca_value.split(',').map(function(item) {
          return item.trim()
        });

        console.log(delete_sid)
        console.log(delete_aca)

        if (delete_index == -1) {
          delete_sid.splice(0, 1);
          delete_aca.splice(0, 1);
        } else {
          delete_sid.splice(delete_index, 1);
          delete_aca.splice(delete_index, 1);
        }

        sibling_aca.value = delete_aca.toString()
        sibling_sid.value = delete_sid.toString()

      });

      function validateSearchForm() {
        var num = /^\d+$/;

        if (document.forms["searchform"]["area"].selectedIndex < 1) {
          alert("지역, 지점을 선택해 주세요.")
          return false;
        } else if (document.forms["searchform"]["time"].value != '') {
          if (num.test(document.forms["searchform"]["time"].value) == false) {
            alert("시간은 숫자만 입력해 주세요.(예:1500)")
            return false;
          }
        }
      }

      function validateTableForm(e) {
        console.log(e)
        tableLength = document.forms[e]['time[]'].length
        tempAddrS = document.forms[e]['addr[]'][0].value
        tempAddrE = document.forms[e]['addr[]'][tableLength - 1].value
        var timepattern = /([01]\d|2[0-3]):([0-5]\d)/;

        if (tempAddrS != "" || tempAddrE != "") {
          alert("시작,끝 주소는 반드시 비워주세요.")
          return false;
        }
        tempTime = document.forms[e]['time[]']
        for (i = 0; i < tableLength; i++) {
          if (timepattern.test(tempTime[i].value) == false) {
            alert(i + 1 + "번째 로우의 숫자를 정확히 입력해 주세요.")
            return false;
          }
        }

        tempName = document.forms[e]['name[]']
        if (tempName[0].value != "" || tempName[tableLength - 1].value != "") {
          alert("시작,끝 이름은 반드시 비워주세요.")
          return false;
        }

        tempLoad = document.forms[e]['load[]']
        for (i = 1; i < tableLength - 1; i++) {
          if (tempLoad[i].value == '') {
            alert(i + 1 + "번째 등하원 여부를 선택해 주세요.")
            return false;
          }
        }

      }

      $( ".table-body" ).sortable({
         update: function( event, ui ){
           $(this).children().each(function(index) {
                $(this).find('td')
              });
            }
      });

}
