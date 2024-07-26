let pendingDeletions = {};

function markImageForDeletion(ideaId, filename, elementId) {
    const element = document.getElementById(elementId);
    element.style.display = 'none'; // 隐藏元素，而不是删除，以便在后端确认删除
    // 将待删除的文件名添加到表单数据中
    const form = document.getElementById(`editForm-${ideaId}`);
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'to_delete_files';
    input.value = filename;
    form.appendChild(input);
}

function handleSubmitEdit(ideaId, event) {
    event.preventDefault(); // 阻止表单默认提交
    const form = document.querySelector(`#editForm-${ideaId}`);
    const formData = new FormData(form);

    // 添加之前在模态框中选择的新文件
    if (window.modalFiles && window.modalFiles[ideaId]) {
        window.modalFiles[ideaId].forEach(file => {
            formData.append('new_files', file);
        });
    }
    // 发送表单数据
    fetch(form.action, {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            alert('修改成功');
            window.location.reload();
        } else {
            alert('修改失败');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert("提交失败");
    });
}

function handleModalFiles(files, ideaId) {
    const previewContainer = document.getElementById(`previewModal-${ideaId}`);
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imgContainer = document.createElement('div');
            imgContainer.classList.add('img-preview-container');

            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = 'auto';
            img.style.height = '50px';

            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = '×';
            deleteBtn.onclick = function() {
                // 移除图片元素
                previewContainer.removeChild(imgContainer);
                // 从文件数组中移除文件
                const fileIndex = newImages.indexOf(file);
                if (fileIndex > -1) {
                    newImages.splice(fileIndex, 1);
                }
            };

            imgContainer.appendChild(img);
            imgContainer.appendChild(deleteBtn);
            previewContainer.appendChild(imgContainer);
        };
        reader.readAsDataURL(file);
        // 如果全局数组newImages不存在，则创建
        if (typeof newImages === 'undefined') {
            window.newImages = [];
        }
        newImages.push(file);
    });
}
