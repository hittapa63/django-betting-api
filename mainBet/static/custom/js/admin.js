var selected_document
$(document).ready(function() {
    $('.change-status').click(function(){
        selected_document = $(this)
        let status = selected_document.attr('status')
        let profile_id = selected_document.attr('profile_id')
        let data = {
            status: status,
            profile_id: profile_id
        }
        AjaxCall(user_update, 'put', data, user_update_response)
    })

    $('.change-bet-status').click(function(){
        selected_document = $(this)
        let status = selected_document.attr('status')
        let bet_id = selected_document.attr('bet_id')
        let data = {
            status: status,
            bet_id: bet_id
        }
        AjaxCall(bet_update, 'put', data, bet_update_response)
    })
})

function ShowMessage(type, message) {
    $.notify({
      icon: "tim-icons icon-bell-55",
      message: message

    }, {
      type: type,
      timer: 3000,
      placement: {
        from: 'top',
        align: 'right'
      }
    });
}

function AjaxCall(url, type, data, response) {
    $.ajax({
        url: url,
        type: type,
        data: data,
        success: response
    })
}

function user_update_response(data, status) {
    if(data.status) {
        user = data.data[0]
        console.log(user)
        if (user.status == 2) {
            Swal.fire(
                'Deleted!',
                'Your file has been deleted.',
                'success'
            ).then(()=> {
                location.reload()
            })
        } else {
            ShowMessage('success', data.message)
            if(user.status == 1) {
                selected_document.attr('status', 0).removeClass('btn-primary').addClass('btn-danger').empty().html('Deactivate')
            } else {
                selected_document.attr('status', 1).removeClass('btn-danger').addClass('btn-primary').empty().html('Activate')
            }
        }
    } else {
        ShowMessage('warning', data.message)
    }
}

function bet_update_response(data, status) {
    if(data.status) {
        bet = data.data[0]
        ShowMessage('success', data.message)
        if(bet.status == 1) {
            selected_document.attr('status', 0).removeClass('btn-primary').addClass('btn-danger').empty().html('Deactivate')
        } else {
            selected_document.attr('status', 1).removeClass('btn-danger').addClass('btn-primary').empty().html('Activate')
        }
    } else {
        ShowMessage('warning', data.message)
    }
}

function UserDelete(profile_id) {
    Swal.fire({
        title: 'Are you sure?',
        text: "This User would be deleted in okbet.",
        type: 'warning',
        showCancelButton: true,
        customClass: {
          confirmButton: 'btn btn-success',
          cancelButton: 'btn btn-danger'
        },
        buttonsStyling: false,
        confirmButtonText: 'Yes, delete it!'
      }).then((result) => {
        if (result.value) {
            data = {
                status: 2,
                profile_id: profile_id,
            }
            AjaxCall(user_update, 'put', data, user_update_response)
        }
    })
}