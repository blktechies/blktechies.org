var blacktechies = angular.module('blacktechies', ['ui.bootstrap']);

blacktechies.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
}]);

blacktechies.controller('CarouselCtrl', function ($scope) {
  $scope.myInterval = 5000;
  var slides = $scope.slides = [];
    $scope.addSlide = function(imageUrl) {
        var newWidth = 1200 + slides.length + 1;
        slides.push({
            image: imageUrl,
            text: ['More','Extra','Lots of','Surplus'][slides.length % 4] + ' ' +
                ['Cats', 'Kittys', 'Felines', 'Cutes'][slides.length % 4]
        });
    };
    for (var i=0; i<6; i++) {
        $scope.addSlide('http://placekitten.com/' + (1201+i) + '/300');
    }
});
