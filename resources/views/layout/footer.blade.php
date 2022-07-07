<style>
    body {
        font-family: "Archivo Black", sans-serif;
        background: #212529;
        display: flex;
        flex-direction: column;
        height: 100vh;
        justify-content: center;
        align-items: center;
        color: #434a51;
    }

    .words {
        color: #212529;
        font-size: 0;
        line-height: 1.5;
    }

    .words span {
        font-size: 4rem;
        display: inline-block;
        animation: move 3s ease-in-out infinite;
    }

    @keyframes move {
        0% {
            transform: translate(-30%, 0);
        }
        50% {
            text-shadow: 0 25px 25px rgba(238, 186, 29, 0.75);
        }
        100% {
            transform: translate(30%, 0);
        }
    }

    .words span:nth-child(2) {
        animation-delay: 0.5s;
    }

    .words span:nth-child(3) {
        animation-delay: 1s;
    }

    .words span:nth-child(4) {
        animation-delay: 1.5s;
    }

    .words span:nth-child(5) {
        animation-delay: 2s;
    }

    .words span:nth-child(6) {
        animation-delay: 2.5s;
    }

    .words span:nth-child(7) {
        animation-delay: 3s;
    }


    .btn-shine {
        color: #212529;
        background: linear-gradient(to right, #4d4d4d 0, rgba(238, 186, 29, 0.75) 10%, #212529 20%) 0;
        background-clip: border-box;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s infinite linear;
        animation-fill-mode: none;
        animation-fill-mode: forwards;
        -webkit-text-size-adjust: none;
        font-weight: 600;
        font-size: 16px;
        text-decoration: none;
        white-space: nowrap;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    @keyframes shine {
        0% {
            background-position: 0;
        }
        60% {
            background-position: 180px;
        }
        100% {
            background-position: 300px;
        }
    }


    h1, h2, h3, h4, h5, h6, i {
        color: rgba(238, 186, 29, 0.75);
        font-weight: bold;
    }


    .copright {
        font-family: 'Teko', sans-serif;
        text-transform: uppercase;
        font-size: 12px;
        text-align: center;
        display: -webkit-flex;
        display: flex;
        -webkit-align-items: center;
        align-items: center;
        -webkit-justify-content: center;
        justify-content: center;
        margin: 0;
        position: relative;
        color: #212529;
        font-weight: bold;
    }

    .copright:before {
        content: attr(data-text);
        position: absolute;
        background: rgba(238, 186, 29, 0.75);
        -webkit-background-clip: text;
        color: transparent;
        background-size: 100% 90%;
        line-height: 0.9;
        clip-path: ellipse(120px 120px at -2.54% -9.25%);
        animation: swing 5s infinite;
        animation-direction: alternate;
    }

    @keyframes swing {
        0% {
            -webkit-clip-path: ellipse(20px 10px at -2.54% -9.25%);
            clip-path: ellipse(20px 20px at -2.54% -9.25%);
        }
        50% {
            -webkit-clip-path: ellipse(20px 20px at 49.66% 64.36%);
            clip-path: ellipse(20px 20px at 49.66% 64.36%);

        }
        100% {
            -webkit-clip-path: ellipse(20px 20px at 102.62% -1.61%);
            clip-path: ellipse(20px 20px at 102.62% -1.61%);
        }
    }


</style>
</body>
</html>
