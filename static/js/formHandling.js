let allFiles = []; // 存储所有文件的数组

function handleFiles(files) {
    Array.from(files).forEach((file, index) => {
        if (!allFiles.some(f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified)) {
            allFiles.push(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                const imgContainer = document.createElement('div');
                imgContainer.className = 'img-preview-container';
                const img = document.createElement('img');
                const deleteBtn = document.createElement('button');

                img.src = e.target.result;
                img.style.width = 'auto';
                img.style.height = '50px';
                
                deleteBtn.textContent = '×';
                deleteBtn.onclick = function() { removeImage(file, imgContainer); };

                imgContainer.appendChild(img);
                imgContainer.appendChild(deleteBtn);
                document.getElementById('preview').appendChild(imgContainer);
            };
            reader.readAsDataURL(file);
        }
    });
}

function removeImage(file, imgContainer) {
    // 查找要删除的文件在数组中的索引
    const index = allFiles.indexOf(file);
    if (index > -1) {
        allFiles.splice(index, 1); // 从数组中移除文件
    }
    imgContainer.remove(); // 移除图片和按钮的容器
}

function handleSubmit(event) {
    event.preventDefault(); // 阻止表单的默认提交行为
    const form = document.querySelector('form');
    const formData = new FormData(form);
    formData.delete('files');
    allFiles.forEach(file => {
        formData.append('files', file); // 确保所有文件都被添加
    });

    fetch(form.action, {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            alert('提交成功');
            allFiles = []; // 清空文件数组以避免重复提交
            document.getElementById('preview').innerHTML = ''; // 清空预览
            window.location.reload();
        } else {
            alert('提交失败');
        }
    }).catch(error => {
        console.error('Error:', error);
        alert("提交失败");
    });
}

function autoResize(textarea) {
    // 清除旧的样式
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}
