function setLocalTimestamp() {
    // 获取当前日期和时间
    var now = new Date();

    // 获取年、月、日
    var year = now.getFullYear();
    var month = (now.getMonth() + 1).toString().padStart(2, '0'); // 月份是从0开始的
    var day = now.getDate().toString().padStart(2, '0');

    // 获取小时、分钟
    var hours = now.getHours().toString().padStart(2, '0'); // 24小时制
    var minutes = now.getMinutes().toString().padStart(2, '0');

    // 组合成需要的格式
    var formattedTimestamp = `${year}-${month}-${day} ${hours}:${minutes}`;

    // 设置隐藏input的值为格式化后的时间
    document.getElementById('localTimestamp').value = formattedTimestamp;
}

// 当文档加载完毕时，绑定事件
document.addEventListener('DOMContentLoaded', function() {
    var form = document.querySelector('form');
    form.addEventListener('submit', setLocalTimestamp);
});
