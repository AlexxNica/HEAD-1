define(['application', 'marionette', 'tpl!./templates/layout.tpl', 'lib/regions/fade_in', 'modules/performances/views/layout',
    'modules/interaction/views/interaction', 'modules/interaction/views/faces', 'jquery', './speech', 'modules/gestures/views/animation_mode',
    'modules/gestures/views/poses', 'modules/gestures/views/animations', './crosshairs', 'scrollbar'],
    function (App, Marionette, template, FadeInRegion, TimelineEditorView, InteractionView, FacesView, $, SpeechView,
              AnimationModeView, PosesView, AnimationsView, CrosshairsView) {
        return Marionette.LayoutView.extend({
            template: template,
            ui: {
                container: '.app-puppeteering-container',
                timeline: '.app-timeline-editor-region',
                controls: '.app-controls',
                leftColumn: '.app-left-column',
                rightColumn: '.app-right-column'
            },
            events: {},
            regions: {
                timeline: {
                    el: ".app-timeline-editor-region",
                    regionClass: FadeInRegion
                },
                animationMode: {
                    el: ".app-animation-mode-region",
                    regionClass: FadeInRegion
                },
                chat: {
                    el: ".app-chat-region",
                    regionClass: FadeInRegion
                },
                poses: {
                    el: '.app-pose-region',
                    regionClass: FadeInRegion
                },
                animations: {
                    el: '.app-animations-region',
                    regionClass: FadeInRegion
                },
                faces: {
                    el: '.app-faces-region',
                    regionClass: FadeInRegion
                },
                crosshairs: {
                    el: '.app-cross-hairs-region',
                    regionClass: FadeInRegion
                },
                speech: {
                    el: '.app-speech-region',
                    regionClass: FadeInRegion
                }
            },
            onAttach: function () {
                var self = this;

                this.ui.leftColumn.perfectScrollbar();
                this.ui.rightColumn.perfectScrollbar();

                // left col
                this.posesView = new PosesView({config: {duration: {min: 1, max: 8}}});
                this.animationModeView = new AnimationModeView();
                this.timelineEditorView = new TimelineEditorView({fluid: true});

                // right col
                this.chatView = new InteractionView({
                    hide_faces: true,
                    recognition_method: 'webspeech',
                    hide_method_select: true,
                    hide_noise: true
                });

                this.crosshairsView = new CrosshairsView();
                this.facesView = new FacesView({always_visible: true});
                this.animationsView = new AnimationsView({config: {speed: {min: 0.5, max: 2}}});
                this.speechView = new SpeechView({interactionView: this.chatView});

                this.getRegion('poses').show(this.posesView);
                this.getRegion('timeline').show(this.timelineEditorView);
                this.getRegion('animationMode').show(this.animationModeView);
                this.getRegion('chat').show(this.chatView);
                this.getRegion('crosshairs').show(this.crosshairsView);
                this.getRegion('faces').show(this.facesView);
                this.getRegion('animations').show(this.animationsView);
                this.getRegion('speech').show(this.speechView);

                var updateDimensions = function () {
                    if (self.isDestroyed)
                        $(window).off('resize', updateDimensions);
                    else
                        self.updateDimensions();
                };

                $(window).on('resize', updateDimensions).resize();
            },
            updateDimensions: function () {
                var height = App.LayoutInstance.getContentHeight();
                this.ui.leftColumn.height(height).perfectScrollbar('update');
                this.ui.rightColumn.height(height).perfectScrollbar('update');
                this.chatView.setHeight(height - this.ui.controls.outerHeight());
            }
        });
    });
