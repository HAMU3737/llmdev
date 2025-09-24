document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const photoInput = document.getElementById("photo");
    const messageInput = document.getElementById("message");
    const sendPhotoBtn = document.getElementById("send-photo");
    const sendChatBtn = document.getElementById("send-chat");
    const sendBothBtn = document.getElementById("send-both");
    const startWorkBtn = document.getElementById("start-work");
    const endWorkBtn = document.getElementById("end-work");

    function appendMessage(text, type = "staff", photoPath = null, address = null) {
        const div = document.createElement("div");
        div.classList.add("chat-message");
        div.classList.add(type === "staff" ? "chat-staff" : "chat-system");
        div.textContent = text;

        if (photoPath) {
            const img = document.createElement("img");
            img.src = photoPath;
            img.classList.add("thumb");
            div.appendChild(document.createElement("br"));
            div.appendChild(img);

            if (address) {
                const addrDiv = document.createElement("div");
                addrDiv.classList.add("photo-address");
                addrDiv.textContent = address || "住所情報なし";
                div.appendChild(addrDiv);
            }
        }

        chatBox.appendChild(div);
        requestAnimationFrame(() => {
            chatBox.scrollTop = chatBox.scrollHeight;
        });
    }

    async function getGeolocation() {
        return new Promise((resolve) => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
                    () => resolve({ latitude: "", longitude: "" })
                );
            } else {
                resolve({ latitude: "", longitude: "" });
            }
        });
    }

    startWorkBtn.addEventListener("click", () => {
        appendMessage("現場に到着しましたか？現場の写真を送ってください。すでに送っている場合は、作業を開始してください。怪我のない様に注意してください。", "system");
    });

    endWorkBtn.addEventListener("click", () => {
        appendMessage("作業お疲れ様でした。作業現場の写真の提出をお願いします。提出がすでに終わっている場合は、作業報告をお願いします。", "system");
    });

    sendPhotoBtn.addEventListener("click", async () => {
        if (!photoInput.files[0]) { alert("写真を選択してください"); return; }
        const formData = new FormData();
        formData.append("photo", photoInput.files[0]);
        const geo = await getGeolocation();
        formData.append("latitude", geo.latitude);
        formData.append("longitude", geo.longitude);

        try {
            const res = await fetch("/report_chat", { method: "POST", body: formData });
            const data = await res.json();
            if (data.reply) appendMessage("写真送信成功", "system", data.photo_path, data.address);
        } catch (err) { appendMessage(`送信エラー: ${err}`, "system"); }
    });

    sendChatBtn.addEventListener("click", async () => {
        const msg = messageInput.value.trim();
        if (!msg) return;
        appendMessage(msg, "staff");
        messageInput.value = "";
        try {
            const res = await fetch("/chat", {
                method: "POST",
                body: new URLSearchParams({ message: msg }),
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });
            const data = await res.json();
            appendMessage(data.reply, "system");
        } catch (err) { appendMessage(`送信エラー: ${err}`, "system"); }
    });

    sendBothBtn.addEventListener("click", async () => {
        const msg = messageInput.value.trim();
        if (!msg && !photoInput.files[0]) { alert("メッセージか写真を入力してください"); return; }
        const formData = new FormData();
        if (photoInput.files[0]) formData.append("photo", photoInput.files[0]);
        if (msg) formData.append("message", msg);
        const geo = await getGeolocation();
        formData.append("latitude", geo.latitude);
        formData.append("longitude", geo.longitude);

        if (msg) appendMessage(msg, "staff");
        messageInput.value = "";
        photoInput.value = "";

        try {
            const res = await fetch("/report_chat", { method: "POST", body: formData });
            const data = await res.json();
            appendMessage(data.reply, "system", data.photo_path, data.address);
        } catch (err) { appendMessage(`送信エラー: ${err}`, "system"); }
    });
});