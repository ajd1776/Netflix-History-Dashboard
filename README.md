<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ajd1776/Netflix-History-Dashboard">
    <img src="./web/public/logo.png" alt="Logo" width="300">
  </a>

<h3 align="center">Netflix History Dashboard</h3>

  <p align="center">
    View your Netflix history on this interactive dashboard.
    <br />
    <a href="https://github.com/ajd1776/Netflix-History-Dashboard"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#usage">Run It Yourself</a>
    ·
    <a href="#Demos">View Demo</a>
    ·
    <a href="https://github.com/ajd1776/Netflix-History-Dashboard/issues">Report Bug</a>
    ·
    <a href="https://github.com/ajd1776/Netflix-History-Dashboard/issues">Request Feature</a>
  </p>
</div>


<!-- PROJECT SHIELDS -->
<p align="center"> 
   <a href="https://github.com/ajd1776/Netflix-History-Dashboard/graphs/contributors">
       <img alt="Contributors" src="https://img.shields.io/github/contributors/ajd1776/Netflix-History-Dashboard.svg?style=for-the-badge"></a>
   <a href="https://github.com/ajd1776/Netflix-History-Dashboard/network/members">
       <img alt="Forks" src="https://img.shields.io/github/forks/ajd1776/Netflix-History-Dashboard.svg?style=for-the-badge"></a>
   <a href="https://github.com/ajd1776/Netflix-History-Dashboard/stargazers">
       <img alt="Stars" src="https://img.shields.io/github/stars/ajd1776/Netflix-History-Dashboard.svg?style=for-the-badge"></a>
   <a href="https://github.com/ajd1776/Netflix-History-Dashboard/issues">
       <img alt="Issues" src="https://img.shields.io/github/issues/ajd1776/Netflix-History-Dashboard.svg?style=for-the-badge"></a>
   <a href="./LICENSE.txt">
       <img alt="License" src="https://img.shields.io/github/license/ajd1776/Netflix-History-Dashboard.svg?style=for-the-badge"></a>
</p>

<p align="center">
  <img alt="Lines" src="https://img.shields.io/tokei/lines/github/ajd1776/Netflix-History-Dashboard?style=flat-square"></a>
  <img alt="Code Size" src="https://img.shields.io/github/languages/code-size/ajd1776/Netflix-History-Dashboard?style=flat-square"></a>
  <img alt="Files" src="https://img.shields.io/github/directory-file-count/ajd1776/Netflix-History-Dashboard?style=flat-square"></a>
</p>


<!-- TABLE OF CONTENTS -->
<details>
  <summary><b>Table of Contents</b></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#features">Features</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project
![image](https://github.com/ajd1776/Netflix-History-Dashboard/assets/48261946/9a1574d3-de84-4caf-923a-ee09e52df5a0)

### Built With
**Analysis (Python):** [pandas](https://pandas.pydata.org) · [FastAPI](https://fastapi.tiangolo.com) · managed with [uv](https://docs.astral.sh/uv/)

**Display (TypeScript):** [React](https://react.dev) · [Vite](https://vite.dev) · hand-drawn SVG charts using [d3-scale](https://d3js.org/d3-scale) and [d3-shape](https://d3js.org/d3-shape) · CSS styled after Apple's Liquid Glass

Python does the parsing, cleaning, classification and aggregation and returns JSON. React only sums the slices it was sent when a filter changes, so the sliders respond instantly. Everything runs on your own computer: the app starts a server that only your machine can reach (`127.0.0.1`), and your history is analysed in memory and never written to disk or sent anywhere.

### Features
- [x] Upload either Netflix export: `NetflixViewingHistory.csv` or the full-data `ViewingActivity.csv` (trailers are skipped).
- [x] UK (`31/12/2023`) and US (`12/31/23`) dates detected automatically.
- [x] Shows and movies told apart, including movies with a colon in the title.
- [x] Totals, active days, longest streak and a monthly timeline of your whole history.
- [x] Highlights: top show, top movie, busiest year, month, weekday and date, biggest day and biggest binge.
- [x] Monthly, day-of-month and day-of-week activity for any year range, plus a month range for day of month.
- [x] Top 3 to 20 shows or movies for any year range.
- [x] Episodes vs movies split.
- [x] A calendar heatmap for each year.
- [x] Recently watched shows and movies.
- [x] Searchable history, filterable by type, with export to an expanded CSV.
- [x] Light and dark mode; respects Reduce Transparency and Reduce Motion.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

Netflix History runs entirely on your own computer. There's no website to sign up to and nothing is uploaded anywhere.

### Mac app

1. Download `Netflix-History-mac.zip` from the [Releases](https://github.com/ajd1776/Netflix-History-Dashboard/releases) page and unzip it.
2. Move **Netflix History.app** to Applications.
3. The app isn't notarised by Apple, so the first time, **right-click it → Open → Open**. After that it opens normally.

Or build it yourself (needs [uv](https://docs.astral.sh/uv/) and Node 20+):

```bash
npm run build:mac   # creates dist/Netflix History.app and dist/Netflix-History-mac.zip
```

### Any computer, in your browser

Needs [uv](https://docs.astral.sh/uv/) and Node 20+.

```bash
git clone https://github.com/ajd1776/Netflix-History-Dashboard.git
cd Netflix-History-Dashboard
npm --prefix web install
npm start           # builds, starts the local server and opens your browser
```

### Development

```bash
npm run dev:api     # terminal 1: API with auto-reload on :8000
npm run dev:web     # terminal 2: web app with hot reload on http://localhost:5173
npm run app         # the Mac window, without packaging
npm test            # pytest + type-checked web build
```

No CSV to hand? Press **Try sample data** for a made-up history.

### Demos (previous version)

https://github.com/ajd1776/Netflix-History-Dashboard/assets/48261946/a1d6ad45-dc70-4984-8b72-68b3cec62867

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
## Roadmap

- [x] Add ability for users to upload thier own history file
- [x] Update UI for dashboard
  - [x] Create responsive layout for all devices
- [ ] Social Media share option
- [ ] Account creation
  - [ ] Compare with other accounts  


See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing
Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


[product-screenshot]: (https://github.com/ajd1776/Netflix-History-Dashboard/assets/48261946/9a1574d3-de84-4caf-923a-ee09e52df5a0)
