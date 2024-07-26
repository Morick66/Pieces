function deleteIdea(ideaId) {
    if (confirm("确认删除这个想法吗？")) {
        fetch(`/delete/${ideaId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert("删除失败");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("删除失败");
        });
    }
}
