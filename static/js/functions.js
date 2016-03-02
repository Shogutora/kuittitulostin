angular.module('lasku', ['ui.bootstrap'])
    .controller('laskuCtrl', function ($scope, $http, $filter) {
        $scope.data = {};
        $scope.loading = false;
        $scope.submitText = "Lähetä";
        $scope.formats = ['EEE dd MMMM yyyy', 'yyyy/MM/dd', 'dd.MM.yyyy', 'shortDate'];
        $scope.format = $scope.formats[0];

        $scope.setDates = function () {
            $scope.data.lpv = $filter('date')(new Date(), $scope.format);
            $scope.data.epv = $filter('date')(new Date(+new Date + 12096e5), $scope.format)
        };
        $scope.setDates();

        $scope.disabled = function (date, mode) {
            return ( mode === 'day' && ( date.getDay() === 0 || date.getDay() === 6 ) );
        };

        $scope.open = function ($event, opened) {
            $event.preventDefault();
            $event.stopPropagation();

            $scope[opened] = true;
        };

        $scope.dateOptions = {
            formatYear: 'yy',
            startingDay: 1,
            showWeeks: false
        };


        $scope.pdfUrl = "";
        $scope.data.tuotteet = [];

        $scope.addRow = function (tuotteet) {
            tuotteet.push({
                id: "",
                kuvaus: "",
                hinta: 0,
                alv: 0,
                halv: 0,
                kpl: 0,
                summa: 0
            })
        };
        $scope.addRow($scope.data.tuotteet);

        $scope.calcPrices = function (tuote) {
            tuote.halv = (tuote.hinta * (1 + tuote.alv / 100));
            tuote.summa = (tuote.halv * tuote.kpl);
        };

        $scope.render = function () {
            $scope.submitText = "Generoi..";
            $scope.loading = true;
            $scope.data.lpv = $filter('date')($scope.data.lpv, $scope.formats[2]);
            $scope.data.epv = $filter('date')($scope.data.epv, $scope.formats[2]);
            $scope.data.veroa = 0;
            $scope.data.veroton = 0;
            $scope.data.yht = 0;

            $scope.data.tuotteet.forEach(function (tuote) {
                $scope.data.veroa += (tuote.hinta * (tuote.alv / 100) * tuote.kpl);
                $scope.data.veroton += (tuote.hinta * tuote.kpl);
                $scope.data.yht += tuote.summa;
                $scope.data.veroa.toFixed(2);
                $scope.data.veroton.toFixed(2);
            });

            $http.post('/render', $scope.data, { responseType: 'arraybuffer' })
                .success(function (data, status, headers, config) {
                    $scope.submitText = "Lähetä";
                    $scope.loading = false;
                    var file = new Blob([data], { type: 'application/pdf' });
                    saveAs(file, "Lasku.pdf");
                })
                .error(function (data, status, headers, config) {
                    $scope.submitText = "Lähetä";
                    $scope.loading = false;
                    console.log("Error in sending")
                });
        };


    });