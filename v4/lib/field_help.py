"""
Settings labels and help text, written for people printing type elements
(not in the vocabulary of the v1/v2 sources they were ported from).
tune_tables._apply_field_text() lays them over SECTIONS_BY_MACHINE, so the
web app and tune.py show the same words.

FIELD_TEXT is each yaml key's wording for every machine; FIELD_TEXT_BY_FAMILY
holds a family's own wording where the same key means something different
there (a "cyl_fn" is the shaft bore on a Blickensderfer, the whole body on
a Hammond). Help is 1-2 plain sentences: what it does, which way to turn
it, and whether it's a real machine measurement.

Help that says "currently has no effect" marks a setting the geometry code
reads but doesn't use (Bennett core_bottom_offset, Helios resin_support_*,
Hammond Split rib_thickness/folder_glue_hole_id_mm) - fix the code or drop
the field, then update the text.
"""

FAMILY_OF = {'blickensderfer': 'cylinder',
 'postal': 'cylinder',
 'mignon': 'mignon_helios',
 'helios': 'mignon_helios',
 'bennett': 'bennett',
 'hammond': 'hammond',
 'hammond_split': 'hammond',
 'selectric12': 'selectric',
 'selectric3': 'selectric',
 'selectric_composer': 'selectric',
 'type_slug': 'slugs',
 'vogue_slug': 'slugs',
 'gauge_slug': 'slugs',
 'oliver_slug': 'slugs',
 'lumi_slug': 'slugs'}

FIELD_TEXT = {
 'gauge_label_size_mm': {'label': 'Label size (mm)',
                         'help': 'Height of the hole diameters engraved on the gauge pockets. Larger is easier to read.'},'a_colon_length_mm': {'label': 'A-to-: span (mm)',
                       'help': 'Distance from the A key to the : key on the middle row, measured on a real card. '
                               'Change only if your keyboard differs.'},
 'aligning_cut_mm': {'label': 'Platen curve position (mm)',
                     'help': 'Where the first platen curve is centered along the slug, measured from the bottom end. '
                             'Move it so the curve lines up with the lowest character.'},
 'alignment_hole_chamfer': {'label': 'Alignment hole chamfer (mm)',
                            'help': 'Size of the bevel at the mouth of each alignment hole, which helps the alignment '
                                    'pin slide in. Larger is more forgiving.'},
 'alignment_hole_depth': {'label': 'Alignment hole depth (mm)',
                          'help': 'How deep each alignment hole goes into the side wall. A real machine measurement; '
                                  'change it only if your machine differs.'},
 'alignment_hole_diameter': {'label': 'Alignment hole diameter (mm)',
                             'help': 'Diameter of the small holes in the side wall, one per character, that the '
                                     "machine's alignment pin seats into. Adjust if the pin fit is too tight or "
                                     'loose.'},
 'alignment_hole_fn': {'label': 'Alignment hole smoothness (segments)',
                       'help': 'Number of segments used to draw each alignment hole. Higher is rounder but slower to '
                               'build, since there is one hole per character.'},
 'angular_divisions': {'label': 'Character slot count',
                       'help': "Number of slots the character spacing is based on: across the shuttle's arc span on "
                               'Hammond, around a full circle on Hammond Split. More slots = closer characters.'},
 'angular_span_deg': {'label': 'Character arc span (deg)',
                      'help': "Total arc the shuttle's character slots cover. With the slot count it sets the angle "
                              'between neighbouring characters. Real machine measurement.'},
 'anvil_id_raw': {'label': 'Anvil bore diameter (mm)',
                  'help': 'Inner bore diameter of the anvil. The drive-pin boss is trimmed to clear it. Real machine '
                          'measurement - change only if yours differs.'},
 'anvil_od': {'label': 'Anvil diameter (mm)',
              'help': "Diameter of the machine's anvil that the shuttle curves around; sets the shuttle's inner "
                      'radius. Real machine measurement - change only if yours differs.'},
 'arc_height': {'label': 'Type arc height (mm)', 'help': 'Height of the type arc band.'},
 'arc_height_offset': {'label': 'Type arc height offset (mm)',
                       'help': "Vertical position of the type arc's bottom edge relative to the base of the hub. "
                               'Negative = lower.'},
 'arc_od': {'label': 'Type arc diameter (mm)',
            'help': 'Outer diameter of the type arc, the curved band that carries the characters. Real machine '
                    'measurement - change only if yours differs.'},
 'arc_thickness': {'label': 'Type arc thickness (mm)', 'help': 'Radial wall thickness of the type arc.'},
 'arrow_enabled': {'label': 'Alignment arrow',
                   'help': "Engraves the small triangle on the top face that marks the element's orientation."},
 'band_depth': {'label': 'Band depth (mm)',
                'help': 'How deep the rings between character rows cut into the facets. Banded style only.'},
 'base_h': {'label': 'Raft thickness (mm)', 'help': 'Thickness of the pad at the foot of each support rod.'},
 'base_od': {'label': 'Raft diameter (mm)',
             'help': 'Diameter of the small pad at the foot of each support rod that sticks to the build plate.'},
 'baseline_mm': {'label': 'Baseline (mm)',
                 'help': 'Distance from the bottom end of the slug to the baseline of the first (lowest) character. '
                         "Change it only if your machine's type sits differently."},
 'baselines_shift_motion_mm': {'label': 'Shift distance between characters (mm)',
                               'help': 'Spacing between the baselines of stacked characters, matching how far the '
                                       'machine moves on shift. Change it only if your machine differs.'},
 'body_fn': {'label': 'Body facets',
             'help': 'Number of facets around the outer wheel body. Higher = rounder but slower.'},
 'body_height_mm': {'label': 'Body height (mm)',
                    'help': 'Depth of the slug from the struck face back to its base. Change it only if your machine '
                            'differs.'},
 'body_length_mm': {'label': 'Body length (mm)',
                    'help': 'Length of the slug from its bottom end to its top end, along the direction the characters '
                            'stack. Change it only if your machine differs.'},
 'body_slot_width_mm': {'label': 'Typebar slot width (mm)',
                        'help': "Width of the slot in the base that fits over the typebar. Set it to your typebar's "
                                'thickness, plus a little clearance for a snug fit.'},
 'body_width_mm': {'label': 'Body width (mm)',
                   'help': "Width of the slug across the face, side to side. Change it only if your machine's type "
                           'slugs differ.'},
 'boss_clearance': {'label': 'Hub clearance (mm)',
                    'help': "Height of the hollow cavity's roof above the hub's bottom face. Controls how much room "
                            'the inside has around the hub.'},
 'boss_od': {'label': 'Hub diameter (mm)',
             'help': 'Outer diameter of the central hub around the shaft hole inside the ball. A real element '
                     'measurement; change it only if yours differs.'},
 'boss_step': {'label': 'Hub step width (mm)',
               'help': 'Widens the hub where it meets the hollow inside. 0 matches the original element.'},
 'boss_to_center_base': {'label': 'Hub face to center (mm)',
                         'help': "Height of the hub's bottom face above the ball's center, before the droop "
                                 'compensation below is added.'},
 'bottom_countersink_depth': {'label': 'Bottom countersink depth (mm)',
                              'help': 'Depth of the recess in the bottom face, where the label is engraved. A real '
                                      'machine measurement; change it only if your machine differs.'},
 'bottom_margin_mm': {'label': 'Bottom margin (mm)',
                      'help': "Distance from the card's bottom edge to the bottom key row."},
 'bottom_support_inner_angle_offset': {'label': 'Hub rod angle offset',
                                       'help': 'Where the rods under the hub sit, as a fraction of the gap between '
                                               'speed holes. 0.5 = midway between holes.'},
 'bottom_thickness_mm': {'label': 'Material above slot (mm)',
                         'help': 'Solid material between the struck face and the top of the typebar slot. More is '
                                 'stronger but leaves less slot depth.'},
 'cap_offset_mm': {'label': 'Capital height offset (mm)',
                   'help': 'Height of the capital letter relative to the circle center. Negative = below center.'},
 'cap_size_mm': {'label': 'Capital letter size (mm)',
                 'help': 'Size of the large capital letter in the middle of each key circle.'},
 'capfig_mod_chars': {'label': 'Capital-row symbols',
                      'help': 'Capital-row characters drawn as symbols, smaller and at their own height, instead of as '
                              'full-size letters.'},
 'capfig_mod_size_mm': {'label': 'Capital-row symbol size (mm)',
                        'help': "Size used instead of the capital size when a key's capital-row character is a symbol "
                                'rather than a letter.'},
 'capfig_offset_mm': {'label': 'Capital-row symbol offset (mm)',
                      'help': 'Height relative to the circle center used instead of the capital offset when the '
                              'capital-row character is a symbol.'},
 'card_border_stroke_mm': {'label': 'Border line width (mm)',
                           'help': "Line width of the card's cut outline in the drawing. Visual only; it does not "
                                   'change the card size.'},
 'card_corner_center_y_mm': {'label': 'Corner arc center height (mm)',
                             'help': "Height of the top corners' rounding center above the card bottom. If the arc "
                                     'ends below the top edge, a straight side fills the gap.'},
 'card_corner_radius_mm': {'label': 'Corner radius (mm)',
                           'help': "Rounding radius of the card's top two corners. The bottom corners stay square."},
 'card_height_mm': {'label': 'Card height (mm)', 'help': 'Overall height of the card.'},
 'card_width_mm': {'label': 'Card width (mm)',
                   'help': 'Overall width of the card, a fixed cut size rather than one fitted to the keys.'},
 'caret_auto_drop': {'label': 'Auto-drop caret',
                     'help': 'Puts the bottom of "^" on the font\'s descender line (the bottom of p, q, g), like the '
                             'low caret of a typewriter face. Caret drop adds to it.'},
 'caret_drop_mm': {'label': 'Caret drop (mm)',
                   'help': 'Moves "^" down (negative = up), on top of auto-drop if that is on. Fonts draw it high as '
                           'an accent; a typewriter caret sits low.'},
 'center_offset_mm': {'label': 'Center offset (mm)',
                      'help': 'Shifts every character sideways in Center mode. Negative = left, positive = right.'},
 'char_enabled': {'label': 'Character enabled',
                  'help': 'Adds the raised struck characters to the slug face. Turned off on the Gauge Slug, which '
                          'carries tick marks instead of a character.'},
 'checker': {'label': 'Checkerboard border',
             'help': "Fills the card's border with a decorative checker pattern. Looks like the original cards but is "
                     'slow to generate.'},
 'circle_diameter_mm': {'label': 'Circle diameter (mm)', 'help': 'Width of each character circle on the card.'},
 'circle_height_bump_mm': {'label': 'Circle height stretch (mm)',
                           'help': 'Makes every circle this much taller than it is wide, giving a slight oval. 0 keeps '
                                   'them round.'},
 'circle_id_mm': {'label': 'Key circle diameter (mm)', 'help': 'Inside diameter of the ring drawn around each key.'},
 'circle_segments': {'label': 'Circle smoothness',
                     'help': 'How many segments make up each drawn circle. Higher = rounder circles and a larger '
                             'file.'},
 'circle_thickness_mm': {'label': 'Key circle line width (mm)',
                         'help': 'Line thickness of the ring drawn around each key.'},
 'clip_bite': {'label': 'Clip bite (mm)',
               'help': "How far the clip wire's seat reaches into the shaft bore. Larger = the wire grips the shaft "
                       'more deeply.'},
 'clip_height': {'label': 'Clip collar height (mm)',
                 'help': "Height of the collar above the wheel's top face that the retaining wire clip snaps onto."},
 'clip_opening': {'label': 'Clip slot opening (mm)',
                  'help': 'Width of the slot the clip wire passes through into its seat.'},
 'clip_to_cell': {'label': 'Clip draft to slot',
                  'help': "Trims each character's draft taper at its own slot edge so it can't run into its neighbor. "
                          'Usually not needed, as the taper stays buried in the wall.'},
 'clip_wire_od': {'label': 'Clip wire diameter (mm)',
                  'help': "Diameter of the machine's retaining wire clip; sets the seat cut in the collar. Change it "
                          'only if your clip differs.'},
 'composer_cap_height': {'label': 'Cap height (pt)',
                         'help': 'Composer sizes type by capital-letter height in points, not by font size; the font '
                                 'size used is this value divided by 2.834. Raise it for larger type.'},
 'core_bottom_offset': {'label': 'Hub bottom offset (mm)',
                        'help': "How far above the element's bottom edge the central hub ends. The underside slopes up "
                                'from the outer wall to meet it.'},
 'core_chamfer': {'label': 'Bore chamfer (mm)',
                  'help': 'Bevel at the ends of the shaft bore, so the wheel slides onto the shaft easily.'},
 'core_contact_length': {'label': 'Shaft contact length (mm)',
                         'help': 'Length at each end of the bore that grips the shaft at full size. The bore is '
                                 'slightly relieved in between to cut friction.'},
 'core_groove_d': {'label': 'Bore groove diameter (mm)',
                   'help': 'Size of each twisted groove in the shaft bore; about half of it cuts into the bore wall. '
                           'Also sets the bore relief between contact zones.'},
 'core_groove_qty': {'label': 'Bore groove count', 'help': 'Number of twisted friction grooves inside the shaft bore.'},
 'core_id_in': {'label': 'Shaft diameter (in)',
                'help': "Diameter of the machine's shaft the wheel slides onto, in inches. Shaft clearance is added on "
                        'top for the printed bore.'},
 'core_id_offset': {'label': 'Shaft clearance (mm)',
                    'help': 'Added to the bore so the print fits over the shaft; larger = looser. Find it with the '
                            'shaft gauge. On Postal it also widens the drive pin hole.'},
 'core_web_length': {'label': 'Hub window length (mm)',
                     'help': 'Height of each upright slot in the hub wall, centered on the hub.'},
 'core_web_qty': {'label': 'Hub window count',
                  'help': 'Number of upright slots cut through the hub wall, spaced evenly around the bore.'},
 'core_web_width': {'label': 'Hub window width (mm)',
                    'help': 'Width of the upright slots cut through the hub wall around the shaft bore.'},
 'corner_fn': {'label': 'Face corner smoothness',
               'help': 'Number of sides used for the rounded face corners. Higher is smoother but slower.'},
 'corner_radius_mm': {'label': 'Corner radius (mm)',
                      'help': "Rounding of the card's four corners. 0 gives square corners."},
 'countersink_diameter': {'label': 'Countersink diameter (mm)',
                          'help': 'Diameter of the shallow round recesses in the top and bottom faces. A real machine '
                                  'measurement; change it only if your machine differs.'},
 'custom_h_chars': {'label': 'Extra horizontal shift: characters',
                    'help': 'Characters listed here get the extra horizontal shift below, for glyphs that sit '
                            'off-center in your font. Leave blank for none.'},
 'custom_h_offset': {'label': 'Extra horizontal shift (mm)',
                     'help': 'Sideways shift added only to the characters listed above. Has no effect while that list '
                             'is blank.'},
 'custom_v_chars': {'label': 'Extra vertical shift: characters',
                    'help': 'Characters listed here get the extra vertical shift below, for glyphs that sit too high '
                            'or low in your font. Leave blank for none.'},
 'custom_v_offset': {'label': 'Extra vertical shift (mm)',
                     'help': 'Up/down shift added only to the characters listed above (positive = up). Has no effect '
                             'while that list is blank.'},
 'cut_groove_diameter': {'label': 'Break-off groove diameter (mm)',
                         'help': 'Size of the round groove cut around the support ring where it meets the element, '
                                 'giving a weak line to snap the support off along.'},
 'cut_groove_thickness': {'label': 'Break-off groove wall (mm)',
                          'help': 'Ring wall left behind the break-off groove. Thinner snaps off more easily; thicker '
                                  'holds the element more securely during printing.'},
 'cyl_fn': {'label': 'Shaft bore facets',
            'help': 'Number of facets around the shaft bore. Higher = rounder fit on the shaft.'},
 'cylinder_bottom_shaft_diameter': {'label': 'Bottom bore diameter (mm)',
                                    'help': 'Diameter of the wide hollow opening at the bottom of the element, which '
                                            'narrows toward the top shaft hole.'},
 'cylinder_shape': {'label': 'Body shape', 'help': '0 = 12-sided body like the original, 1 = round body.'},
 'cylinder_top_chamfer': {'label': 'Top chamfer size (mm)',
                          'help': 'Width of the sloped ring at the base of the top boss that the logo and label text '
                                  'sit on.'},
 'cylinder_top_diameter': {'label': 'Top boss diameter (mm)',
                           'help': 'Diameter of the narrower boss on top of the main body. A real machine measurement; '
                                   'change it only if your machine differs.'},
 'cylinder_top_height_offset': {'label': 'Top boss height (mm)',
                                'help': 'Height of the narrower boss on top of the main body, where the logo and label '
                                        'sit. A real machine measurement; change it only if your machine differs.'},
 'cylinder_top_shaft_diameter': {'label': 'Top shaft hole diameter (mm)',
                                 'help': 'Diameter of the shaft hole through the top of the element. Must fit your '
                                         "machine's shaft; adjust slightly if the print is too tight or loose."},
 'del_base_from_centre': {'label': 'Arrow distance from center (mm)',
                          'help': 'How far the alignment arrow sits from the center of the top face.'},
 'del_depth': {'label': 'Label and arrow depth (mm)',
               'help': 'How deep the labels and alignment arrow are engraved into the top face. Deeper reads better '
                       'but leaves less material.'},
 'depth_mm': {'label': 'Label depth (mm)',
              'help': 'How deep the label text is cut into the part. Deeper reads better but weakens thin walls.'},
 'detent_skirt_clock_offset': {'label': 'Detent teeth rotation (deg)',
                               'help': 'Rotates the detent teeth around the skirt to line them up with the characters. '
                                       '0 matches the original element.'},
 'detent_valley_to_center': {'label': 'Detent tooth position (mm)',
                             'help': 'Sets how far out the detent teeth under the skirt sit from the center. A real '
                                     'element measurement; change it only if yours differs.'},
 'draft_angle_deg': {'label': 'Draft angle (deg)',
                     'help': "How steeply each character's walls flare out toward the base. Larger = wider, sturdier "
                             'base. Only applied on Render; Quick Preview skips it.'},
 'drive_notch_height': {'label': 'Drive notch height (mm)',
                        'help': 'Height of the drive notch inside the hub. A real measurement; change it only if yours '
                                'differs.'},
 'drive_notch_theta': {'label': 'Drive notch angle (deg)',
                       'help': 'Where the drive notch sits around the shaft, which sets how the characters line up '
                               'with the machine. Change it only if your element differs.'},
 'drive_notch_width': {'label': 'Drive notch width (mm)',
                       'help': "Width of the notch inside the hub that keys the element to the machine's post. A real "
                               'measurement; change it only if yours differs.'},
 'drive_pin_countersink_depth': {'label': 'Drive pin countersink depth (mm)',
                                 'help': 'Depth of the round recess around the drive pin hole on the underside.'},
 'drive_pin_length': {'label': 'Drive pin length (mm)',
                      'help': 'Length of the drive pin hole. A real machine measurement; change it only if your '
                              'machine differs.'},
 'drive_pin_length_old': {'label': 'Early slot length (mm)',
                          'help': 'Length of the Early-style drive slot, also used as its countersink diameter. Only '
                                  'used when Drive pin style is Early.'},
 'drive_pin_length_start_old': {'label': 'Early slot inner radius (mm)',
                                'help': "Distance from the wheel's center to the inner end of the Early-style slot. "
                                        'Only used when Drive pin style is Early.'},
 'drive_pin_radial': {'label': 'Drive pin distance from center (mm)',
                      'help': "Distance from the wheel's center to the drive pin hole. A real machine measurement; "
                              'change it only if your machine differs.'},
 'drive_pin_style': {'label': 'Drive pin style',
                     'help': 'Which drive fitting to cut: Later is a rectangular pin hole, Early a radial slot. '
                             'Changes the hole, countersink boss and resin support together.'},
 'drive_pin_support_height': {'label': 'Countersink boss height (mm)',
                              'help': 'How far the solid boss around the countersink rises above it inside the hollow '
                                      'body.'},
 'drive_pin_support_radial_offset': {'label': 'Countersink boss wall (mm)',
                                     'help': 'Thickness of solid material left around the drive pin countersink inside '
                                             'the hollow body. Thicker = stronger boss.'},
 'drive_pin_width_offset': {'label': 'Drive pin clearance (mm)',
                            'help': "Added to the drive pin hole's width so the print fits over the pin. Larger = "
                                    'looser fit.'},
 'drive_pin_width_oldmm': {'label': 'Early slot width (mm)',
                           'help': 'Width of the Early-style drive slot, before drive pin clearance is added. Only '
                                   'used when Drive pin style is Early.'},
 'drive_pin_widthmm': {'label': 'Drive pin width (mm)',
                       'help': "Width of the hole for the machine's drive pin, before clearance is added. A real "
                               'machine measurement; change it only if yours differs.'},
 'edge_gap': {'label': 'Edge gap (mm)',
              'help': "Vertical printing only: pulls the support rows at the shuttle's top and bottom edges inward by "
                      'this much.'},
 'edge_to_column_mm': {'label': 'Edge to first column (mm)',
                       'help': "Distance from the card's side edge to the center of the first column of circles. The "
                               'remaining columns are spaced evenly across the card.'},
 'edge_to_row_mm': {'label': 'Edge to first row (mm)',
                    'help': "Distance from the card's top or bottom edge to the center of the first row of circles. "
                            'The remaining rows are spaced evenly down the card.'},
 'element_clip_angle': {'label': 'Clip angle (deg)', 'help': 'Rotates the wire clip channel around the shaft.'},
 'element_clip_bite': {'label': 'Clip bite (mm)',
                       'help': 'How far the wire channel overlaps into the shaft hole, so the wire presses on the '
                               'shaft. More bite grips tighter.'},
 'element_clip_diameter': {'label': 'Clip boss diameter (mm)',
                           'help': 'Diameter of the round boss on top of the element that holds the wire retaining '
                                   'clip.'},
 'element_clip_height': {'label': 'Clip boss height (mm)',
                         'help': 'Height of the round boss on top of the element that holds the wire retaining clip.'},
 'element_diameter': {'label': 'Element diameter (mm)',
                      'help': 'Outer diameter of the wheel body, not counting the raised characters. A real machine '
                              'measurement; change it only if your machine differs.'},
 'element_height': {'label': 'Element height (mm)',
                    'help': 'Height of the wheel body, not counting the clip collar on top. A real machine '
                            'measurement; change it only if your machine differs.'},
 'element_indicator_hole_diameter': {'label': 'Indicator hole diameter (mm)',
                                     'help': 'Diameter of the small indicator hole in the top.'},
 'element_indicator_hole_position': {'label': 'Indicator hole distance from center (mm)',
                                     'help': 'How far the small indicator hole in the top sits from the shaft center.'},
 'element_inside_radius': {'label': 'Inside corner radius (mm)',
                           'help': 'Rounding of the corners inside the hollow element.'},
 'element_shell_thickness': {'label': 'Shell thickness (mm)',
                             'help': "Wall thickness of the hollow element's top, bottom and sides. Thicker is "
                                     'stronger but heavier.'},
 'element_square_hole_length': {'label': 'Alignment hole length (mm)',
                                'help': 'Length of the rectangular alignment hole in the bottom. Change it only if '
                                        'your machine differs.'},
 'element_square_hole_position': {'label': 'Alignment hole distance from center (mm)',
                                  'help': 'How far the rectangular alignment hole sits from the shaft center. A real '
                                          'machine measurement; change it only if your machine differs.'},
 'element_square_hole_support_height': {'label': 'Alignment hole boss height (mm)',
                                        'help': 'Height of a raised boss around the alignment hole. The boss is '
                                                'currently switched off, so this has no effect.'},
 'element_square_hole_width': {'label': 'Alignment hole width (mm)',
                               'help': 'Width of the rectangular alignment hole in the bottom. Change it only if your '
                                       'machine differs.'},
 'element_wire_diameter': {'label': 'Clip wire diameter (mm)',
                           'help': 'Diameter of the spring wire that retains the element on the shaft. Match your '
                                   "machine's wire."},
 'enabled': {'label': 'Typeface label',
             'help': 'Engraves the typeface name into the flat top of the ball, like the name stamped on original '
                     'elements.'},
 'face_radius_mm': {'label': 'Face corner radius (mm)',
                    'help': 'Rounding on the four corners of the face plate. Larger gives softer corners.'},
 'face_thickness_mm': {'label': 'Face plate thickness (mm)',
                       'help': 'Thickness of the flat, full-width plate behind the characters before the body narrows '
                               'toward the base.'},
 'fence_angle_deg': {'label': 'Bracing angle (deg)', 'help': 'Angle of the diagonal bracing rods between supports.'},
 'fence_spacing': {'label': 'Bracing spacing (mm)',
                   'help': 'Spacing of the diagonal rods that brace the supports together under the type arc. Smaller '
                           '= stiffer support, more cleanup.'},
 'fig_dupe_chars': {'label': 'Blank figure characters',
                    'help': 'Figure-row characters treated as placeholders and left blank on the card.'},
 'fig_dupe_offset_mm': {'label': 'Blank-figure capital shift (mm)',
                        'help': 'Extra height added to the capital letter on keys whose figure position is left blank, '
                                'filling the empty space.'},
 'fig_offset_mm': {'label': 'Figure height offset (mm)',
                   'help': "How far above the key circle's center the small figure character sits."},
 'fig_size_mm': {'label': 'Figure / lowercase size (mm)',
                 'help': 'Size of the small figure character above each capital, and of the lowercase or punctuation '
                         'character below it.'},
 'fine_pitch_mm': {'label': 'Fine tick spacing (mm)',
                   'help': 'Distance between the short fine tick marks along the side edge of the gauge.'},
 'fine_z_mm': {'label': 'Fine tick length (mm)',
               'help': 'Where the fine ticks end, measured from the face (negative goes back toward the base). More '
                       'negative makes them longer.'},
 'finger_thickness': {'label': 'Finger notch width (mm)',
                      'help': "Width of the notch at the start of the type arc that the machine's alignment finger "
                              'engages.'},
 'flatness_tolerance_mm': {'label': 'Curve smoothness tolerance (mm)',
                           'help': "How far straight segments may stray from a character's true curves. Smaller = "
                                   'smoother curves but slower builds; larger = faster, more faceted.'},
 'floor': {'label': 'Center to detent tooth tips (mm)',
           'help': "Distance from the ball's center down to the tips of the detent teeth, which sets the skirt height. "
                   'Measured from a real element; change it only if yours differs.'},
 'folder_close_gap': {'label': 'Hub seam gap (deg)',
                      'help': "Angular gap left at the seam between the two halves' hub sections; each kept section "
                              'starts at half this angle.'},
 'folder_degree_offset': {'label': 'Spoke start angle (deg)',
                          'help': 'Rotates the spokes and stiffening rib around the hub, and moves the end of the kept '
                                  'hub section with them.'},
 'folder_degrees': {'label': 'Hub section angle (deg)',
                    'help': 'Angular width of the hub section each half keeps. The rest is cut away so the other '
                            "half's hub can nest in."},
 'folder_glue_groove_depth': {'label': 'Glue groove depth (mm)',
                              'help': 'How far the glue groove reaches past the shaft bore wall.'},
 'folder_glue_groove_r': {'label': 'Glue groove radius (mm)',
                          'help': 'Radius of the round glue groove cut around the shaft bore inside the hub.'},
 'folder_glue_hole_id_mm': {'label': 'Glue hole diameter (mm)',
                            'help': "Intended diameter of the hub's glue holes. Currently has no effect: the holes are "
                                    'built at a fixed 0.8 mm.'},
 'folder_id_mm': {'label': 'Hub joint diameter (mm)',
                  'help': "Diameter where the two halves' hubs nest together. The hub radial gap is added on one half "
                          'and taken off the other.'},
 'folder_od': {'label': 'Hub diameter (mm)', 'help': 'Outer diameter of the central hub.'},
 'folder_radial_gap': {'label': 'Hub radial gap (mm)',
                       'help': "Clearance where the two hubs nest: added to one half's joint diameter and taken off "
                               "the other's."},
 'folder_squash_clearance': {'label': 'Hub thickness clearance (mm)',
                             'help': "Clearance between the two hub halves across the thickness, so they don't bind "
                                     'when pressed together.'},
 'folder_thickness': {'label': 'Hub thickness (mm)',
                      'help': 'Total thickness of the hub with both halves fitted together. Real machine measurement - '
                              'change only if yours differs.'},
 'font2_chars': {'label': 'Second font characters',
                 'help': 'Characters struck in the second font instead of the main one.'},
 'font2_composer_cap_height': {'label': 'Font 2 cap height (pt)',
                               'help': 'Cap height in points for the characters drawn from the second font, sized the '
                                       'same way as the main cap height.'},
 'font2_path': {'label': 'Second font',
                'help': 'A second font for the characters listed under Second font characters - e.g. fractions or '
                        'symbols your main font lacks. Blank uses the main font.'},
 'font2_size_mm': {'label': 'Second font size (mm)',
                   'help': "Size of the second font's characters. 0 = the same as the main font."},
 'font_label_offset': {'label': 'Typeface label offset (mm)',
                       'help': 'Nudges the typeface label across the top face to fine-tune where it sits.'},
 'font_label_size': {'label': 'Typeface label size (mm)',
                     'help': 'Text size of the engraved typeface name. Shrink it if a long name runs off the top '
                             'face.'},
 'font_path': {'label': 'Logo font file', 'help': 'Font for the logo text engraved on the top face.'},
 'gauge_hole_fn': {'label': 'Tick hole smoothness',
                   'help': "Number of sides used for the gauge's tick holes. Higher is rounder but slower."},
 'groove_fn': {'label': 'Bore groove facets',
               'help': "Number of segments around each twisted bore groove's cross-section. Higher = smoother grooves, "
                       'slower build.'},
 'groove_od': {'label': 'Breakaway groove diameter (mm)',
               'help': 'Size of the two score grooves in the support ring under the outer wall. Larger = easier to '
                       'snap off, weaker ring.'},
 'groove_opening_offset': {'label': 'Groove opening extra height (mm)',
                           'help': 'Builds without a rib: extra height given to the wall opening beyond the slot '
                                   'itself, split above and below.'},
 'groove_tab_width': {'label': 'Groove opening width (mm)',
                      'help': 'Builds without a rib, and the separate rib part: width of the opening through the '
                              "shuttle wall where the rib's tang plugs in."},
 'groove_thickness': {'label': 'Breakaway web thickness (mm)',
                      'help': 'Thickness of the ring material beside the breakaway grooves. Thicker = sturdier ring, '
                              'harder to snap off.'},
 'height_increase_mm': {'label': 'Tall type extra height (mm)',
                        'help': 'Added to the element height when tall display type is on.'},
 'height_offset_mm': {'label': 'Logo lift (mm)',
                      'help': 'Pushes the logo out from the curved chamfer it sits on. Raising it usually needs more '
                              'extrusion depth too, or characters away from the center stay buried.'},
 'hole_d_mm': {'label': 'Tick width (mm)',
               'help': 'Diameter of the grooves cut into the side edge that form the tick marks. Wider marks are '
                       'easier to see.'},
 'hole_fn': {'label': 'Tick hole smoothness',
             'help': "Number of sides used for the gauge's tick holes. Higher is rounder but slower."},
 'id_offset': {'label': 'Hole fit allowance (mm)',
               'help': 'Extra diameter added to the shaft bore, pin holes and glue holes for print fit. Raise it if '
                       'they print too tight.'},
 'indicator_diameter': {'label': 'Indicator hole diameter (mm)',
                        'help': 'Diameter of the small marker hole in the top face near the edge. A real machine '
                                'measurement; change it only if your machine differs.'},
 'inner_border': {'label': 'Inner border',
                  'help': 'Draws an extra line around the grid of character circles. Off by default, matching the '
                          'original cards.'},
 'inset': {'label': 'Tip embed depth (mm)',
           'help': 'How far each tip sinks into the part. Deeper = firmer hold, bigger mark when removed.'},
 'inside_id': {'label': 'Hollow inside diameter (mm)',
               'help': 'Diameter of the hollow cavity inside the ball, seen from underneath. A real element '
                       'measurement; change it only if yours differs.'},
 'interval': {'label': 'Sweep step (mm)',
              'help': 'Added for each column after the first, so column n tests start + n x step.'},
 'label1': {'label': 'Label line 1',
            'help': 'First line of engraved label text, for example your name. Leave blank for none.'},
 'label1a': {'label': 'Label 1a (top line, right group)',
             'help': 'Upper line of the two-line text engraved on one side of the shaft, e.g. a first name. Leave '
                     'blank to skip it.'},
 'label1a_radial_mm': {'label': 'Label 1a distance from center (mm)',
                       'help': 'How far the center of label 1a sits from the shaft center. Increase to move it '
                               'outward, away from the shaft hole.'},
 'label1b': {'label': 'Label 1b (bottom line, right group)',
             'help': 'Lower line of the two-line text engraved on one side of the shaft, e.g. a last name. Leave blank '
                     'to skip it.'},
 'label1b_radial_mm': {'label': 'Label 1b distance from center (mm)',
                       'help': 'How far the center of label 1b sits from the shaft center. Increase to move it '
                               'outward, away from the shaft hole.'},
 'label2': {'label': 'Label line 2',
            'help': 'Second line of engraved label text, for example a year. Leave blank for none.'},
 'label2_radial_mm': {'label': 'Label 2 distance from center (mm)',
                      'help': 'How far the center of label 2 sits from the shaft center. Negative puts it on the '
                              'opposite side from labels 1a and 1b.'},
 'label_depth_mm': {'label': 'Copyright engraving depth (mm)',
                    'help': 'How deep the side text is cut into the slug. Deeper reads more clearly but weakens thin '
                            'walls.'},
 'label_font_override': {'label': 'Typeface label font',
                         'help': 'Font file used for the typeface label. Leave blank to use the main font.'},
 'label_font_path': {'label': 'Label font',
                     'help': "Font file used for the raised label text on the element's top chamfer."},
 'label_height_offset_mm': {'label': 'Label lift (mm)',
                            'help': 'Pushes the label out from the curved chamfer it sits on. Raising it usually needs '
                                    'more extrusion depth too, or characters away from the center stay buried.'},
 'label_no': {'label': 'Number label text',
              'help': 'Text of the number label, usually the pitch such as "10" or "12".'},
 'label_no_font_override': {'label': 'Number label font',
                            'help': 'Font file used for the number label. Leave blank to use the main font.'},
 'label_size_mm': {'label': 'Label text size (mm)', 'help': 'Height of the engraved label lettering.'},
 'label_text': {'label': 'Label text',
                'help': 'A second line of raised text, placed directly opposite the logo. Leave blank for none; keep '
                        'it short so it does not run into the logo.'},
 'label_text_depth_mm': {'label': 'Label extrusion depth (mm)',
                         'help': 'How thick the raised label text is. Thicker text is easier to see and survives the '
                                 "chamfer's curve better; too thin and most of it stays buried."},
 'label_text_override': {'label': 'Typeface label text',
                         'help': "Text engraved as the typeface name. Leave blank to use the font's own name."},
 'label_text_size_mm': {'label': 'Label text size (mm)',
                        'help': 'Height of the label characters. Keep it small enough that the text fits on the narrow '
                                'chamfer.'},
 'label_text_spacing': {'label': 'Label character spacing (deg)',
                        'help': 'Angle between neighbouring label characters around the ring. Larger spreads the text '
                                'further around the element.'},
 'left_margin_mm': {'label': 'Left margin (mm)',
                    'help': "Distance from the card's left edge to the first key of each row. All three rows start in "
                            'the same column.'},
 'left_offset_mm': {'label': 'Left offset (mm)',
                    'help': 'Shifts every character sideways in Left mode. Negative = left, positive = right; 0 keeps '
                            "the font's own position."},
 'legend_flatness_tolerance_mm': {'label': 'Glyph outline tolerance (mm)',
                                  'help': 'How closely letter curves on the card are followed. Smaller = smoother; a '
                                          'paper card needs far less precision than a struck element.'},
 'legend_font_path': {'label': 'Legend font path',
                      'help': 'Font for the printed key-chart card. Independent of the type font, since the card is '
                              'printed on paper or laser-cut, not struck.'},
 'legend_height_offset_mm': {'label': 'Circle center to baseline (mm)',
                             'help': "How far each character's baseline sits below its circle's center. Raise it to "
                                     'move the characters down inside the circles.'},
 'length_mm': {'label': 'Card length (mm)', 'help': 'Overall length of the index card.'},
 'line_width_mm': {'label': 'Ring and border line width (mm)',
                   'help': 'Stroke width of the circle rings and the card border.'},
 'location_frac': {'label': 'Logo position (fraction of body length)',
                   'help': 'Where the logo sits along the slug, from 0 at the bottom end to 1 at the top end.'},
 'logo_depth_mm': {'label': 'Logo engraving depth (mm)', 'help': 'How deep the logo is cut into the top face.'},
 'logo_enabled': {'label': 'SVG logo',
                  'help': "Cuts a vector logo into the element's top face. Off by default because the logo is large "
                          'for this element; check its size and position before printing.'},
 'loop_diameter_mm': {'label': 'Loop outer diameter (mm)',
                      'help': 'Outside diameter of the ring. By default it matches the body width.'},
 'loop_enabled': {'label': 'Loop enabled',
                  'help': 'Adds a ring at the top end of the slug so it can hang as a pendant or keychain.'},
 'loop_fn': {'label': 'Loop smoothness (around)',
             'help': 'Number of steps around the ring. Higher is smoother but slower.'},
 'loop_rotation_deg': {'label': 'Loop rotation (deg)',
                       'help': "Turns the ring around the slug's long axis. 0 lays it flat; 90 stands it on edge."},
 'loop_thickness_mm': {'label': 'Loop tube thickness (mm)',
                       'help': "Thickness of the ring's wire. Thicker is sturdier but leaves a smaller opening."},
 'loop_tube_fn': {'label': 'Loop smoothness (wire)',
                  'help': "Number of sides on the ring's wire cross-section, set separately from the steps around. "
                          'Higher is smoother but can make the file much larger.'},
 'lower_char': {'label': 'Lower character',
                'help': 'The character typed without shift. It sits nearer the bottom end of the slug, at the '
                        'baseline.'},
 'lower_wing_angle_deg': {'label': 'Lower wing angle (deg)',
                          'help': 'Tilts the bottom end wall of the slug inward toward the base. 0 gives a square '
                                  'end.'},
 'lowercase_mod_chars': {'label': 'Lowercase characters to draw',
                         'help': 'The only lowercase-row characters drawn as their own small label. The rest are '
                                 'skipped since they repeat the capital letter.'},
 'lowercase_offset_mm': {'label': 'Lowercase height offset (mm)',
                         'help': 'Height of the lowercase or punctuation character relative to the circle center. '
                                 'Negative = below center.'},
 'major_pitch_mm': {'label': 'Major tick spacing (mm)',
                    'help': 'Distance between the long major tick marks along the side edge of the gauge.'},
 'major_z_mm': {'label': 'Major tick length (mm)',
                'help': 'Where the major ticks end, measured from the face (negative goes back toward the base). Set '
                        'it past the fine ticks so major marks stand out.'},
 'math_shuttle_height': {'label': 'Math shuttle height (mm)',
                         'help': 'Height of the taller four-row Math shuttle, used automatically when the layout has '
                                 'four rows. Real machine measurement.'},
 'min_band_height_mm': {'label': 'Min wall band height (mm)',
                        'help': 'The wall is split into horizontal bands so attaching the characters builds cleanly. '
                                'Bands are never shorter than this; 0 = automatic.'},
 'min_final_character_diameter': {'label': 'Character face diameter (mm)',
                                  'help': 'Diameter across the faces of the raised characters. They stand out from the '
                                          'body by half the difference from element diameter.'},
 'min_rod_h': {'label': 'Min rod height (mm)',
               'help': 'Gap between the build plate and the lowest point of the element, giving room to cut supports '
                       'off cleanly.'},
 'min_rod_height': {'label': 'Lift above raft (mm)',
                    'help': 'Gap between the bottom of the element and the top of the raft. Larger = taller supports '
                            'and more room to cut them off.'},
 'minkowski_cone_height_mm': {'label': 'Draft taper height (mm)',
                              'help': "Height of the tapered base below each character's face. It must reach into the "
                                      'body so wide characters root firmly; taller is the safer direction.'},
 'minkowski_enabled': {'label': 'Draft taper',
                       'help': 'Gives each character its tapered, strong base. Turn off for a fast preview with '
                               'correct placement and platen curve but no taper; leave on for printing.'},
 'minkowski_fn': {'label': 'Draft taper facets',
                  'help': 'Facets on the draft taper around each character. Together with curve tolerance, the biggest '
                          'factor in build time; lower = faster.'},
 'minkowski_text': {'label': 'Tapered logo and label text',
                    'help': 'Gives both logo and label text the same sloped sides as the struck characters. Off uses '
                            'plain straight-sided text, which builds faster.'},
 'mode': {'label': 'Horizontal alignment',
          'help': "Center places each character on the middle of its advance width; Left starts it at the font's own "
                  'left edge.'},
 'modified_left_chars': {'label': 'Extra-shift characters (group 1)',
                         'help': 'Characters that get their own sideways shift on top of the normal alignment - '
                                 'usually punctuation that sits off-centre.'},
 'modified_left_offset_mm': {'label': 'Extra shift, group 1 (mm)',
                             'help': 'Sideways shift for the group 1 characters. Negative = left, positive = right.'},
 'modified_right_chars': {'label': 'Extra-shift characters (group 2)',
                          'help': 'A second group of characters with its own sideways shift. A character in both '
                                  'groups uses group 1.'},
 'modified_right_offset_mm': {'label': 'Extra shift, group 2 (mm)',
                              'help': 'Sideways shift for the group 2 characters. Negative = left, positive = right.'},
 'no_label_offset': {'label': 'Number label offset (mm)',
                     'help': 'Nudges the number label along the top face to fine-tune where it sits.'},
 'no_label_size': {'label': 'Number label size (mm)', 'help': 'Text size of the engraved number label.'},
 'normal_shuttle_height': {'label': 'Shuttle height (mm)',
                           'help': 'Height of a standard three-row shuttle. Real machine measurement - change only if '
                                   'yours differs.'},
 'notch_diameter': {'label': 'Notch diameter (mm)',
                    'help': 'Width of the groove cut at each facet corner. Notched style only.'},
 'notch_extension': {'label': 'Notch extension (mm)',
                     'help': 'How far the notch cut reaches outward past the facet corner, so it also trims the '
                             "characters' flared bases. Notched style only."},
 'notch_fn': {'label': 'Notch facets',
              'help': 'Facets on each notch groove (Notched style only). A tiny groove needs few; raise it only if '
                      'notches look polygonal.'},
 'offset_int': {'label': 'Pocket step (mm)',
                'help': 'How much each outer pocket grows over the one before. Every pocket is engraved with its '
                        'actual hole diameter.'},
 'offset_start': {'label': 'First pocket offset (mm)',
                  'help': 'How much bigger than the current fit (shaft + clearance, the unlabeled centre hole) the '
                          'first outer pocket bores. Negative starts below it, so the pockets bracket the current fit.'},
 'outer_inset_mm': {'label': 'Logo inset from edge (mm)',
                    'help': 'How far in from the outer edge the logo sits. Larger = closer to the center.'},
 'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                       'help': 'The build log flags downward faces, and Selectric glyph rows, shallower than this '
                               'above horizontal. 30 is a cautious resin starting point.'},
 'path': {'label': 'Font file', 'help': 'The TrueType or OpenType font the struck characters are made from.'},
 'pin_depth': {'label': 'Alignment slot depth (mm)',
               'help': 'How far the alignment slot cuts into the wall beyond the bottom bore.'},
 'pin_height': {'label': 'Alignment slot height (mm)',
                'help': 'Height of the rounded alignment slot cut into the bottom bore, which keys the element onto '
                        'the machine. Change it only if your machine differs.'},
 'pin_id_chamfer': {'label': 'Pin hole chamfer (mm)',
                    'help': 'Chamfer on the edges of the drive-pin holes and the glue hole openings.'},
 'pin_id_mm': {'label': 'Pin hole diameter (mm)',
               'help': 'Diameter of the two drive-pin holes through the hub, before the print-fit allowance. Real '
                       'machine measurement.'},
 'pin_radial': {'label': 'Pin hole distance (mm)',
                'help': 'Distance from the hub center to the drive-pin holes. Real machine measurement - change only '
                        'if yours differs.'},
 'pin_through': {'label': 'Slot all the way through',
                 'help': 'Cuts the alignment slot right through the outer wall instead of stopping inside it.'},
 'pin_width': {'label': 'Alignment slot width (mm)',
               'help': 'Width of the rounded alignment slot cut into the bottom bore. Change it only if your machine '
                       'differs.'},
 'platen_diameter': {'label': 'Platen diameter (mm)',
                     'help': "Diameter of your typewriter's platen roller. Each character face is curved to match it. "
                             'Change it only if your machine differs.'},
 'platen_diameter_mm': {'label': 'Platen diameter (mm)',
                        'help': 'Diameter of your platen roller. The character faces are curved to match it. Change it '
                                'only if your machine differs.'},
 'platen_fn': {'label': 'Platen cutout facets',
               'help': 'Facets on the platen-shaped curve cut into each character face. Higher = smoother face curve, '
                       'slower build.'},
 'platen_shift_motion_mm': {'label': 'Platen shift motion (mm)',
                            'help': 'Spacing between the platen curves cut into the characters, one per character. '
                                    'Match it to the shift distance unless your machine differs.'},
 'position_offset_deg': {'label': 'Logo position (deg)',
                         'help': 'Where around the top face the logo is centered. Changing it swings the whole logo '
                                 'around the wheel.'},
 'positioner_pin_diameter': {'label': 'Positioner pin hole diameter (mm)',
                             'help': "Diameter of the two holes that fit the machine's positioner pins. Adjust "
                                     'slightly if the element fits too tight or too loose on the pins.'},
 'positioner_pin_radius': {'label': 'Positioner pin distance from center (mm)',
                           'help': 'Distance from the shaft center to each positioner pin hole. A real machine '
                                   'measurement; change it only if your machine differs.'},
 'post_enabled': {'label': 'Mounting post enabled',
                  'help': 'Adds a collar inside the typebar slot near the top end, with a cross hole for a pin or '
                          'screw to hold the slug on.'},
 'post_fn': {'label': 'Post smoothness',
             'help': 'Number of sides used for the mounting post and its hole. Higher is smoother but slower.'},
 'post_id_mm': {'label': 'Post hole diameter (mm)',
                'help': 'Diameter of the cross hole through the mounting post. Set it to fit your pin or screw.'},
 'post_od_mm': {'label': 'Post collar size (mm)',
                'help': 'How far the collar around the post hole extends. Larger gives a thicker, stronger ring of '
                        'material around the hole.'},
 'pre_minkowski_char_height_mm': {'label': 'Character face height (mm)',
                                  'help': "Height of each character's straight-walled top part, above the draft taper. "
                                          'On wheels it plus cone height sets character depth; elsewhere any ample '
                                          'value works.'},
 'qp_length_mm': {'label': 'Q-to-P span (mm)',
                  'help': 'Distance from the Q key to the P key on the top row, measured on a real card. Change only '
                          'if your keyboard differs.'},
 'radial_offset_mm': {'label': 'Label distance from center (mm)',
                      'help': 'How far from the hub center the two label lines sit, measured along the first spoke. '
                              'Move it if the text runs off the spoke.'},
 'raft': {'label': 'Continuous raft',
          'help': 'Off: each rod gets its own small raft foot. On: one solid raft plate under all the rods, reaching '
                  "the element's center."},
 'raft_od': {'label': 'Rod foot diameter (mm)',
             'help': 'Diameter of the small raft under each rod when Continuous raft is off. Larger = better bed '
                     'adhesion.'},
 'raft_thickness': {'label': 'Raft thickness (mm)',
                    'help': 'Thickness of the raft feet, continuous raft plate and outer support ring base.'},
 'raft_thickness_mm': {'label': 'Raft thickness (mm)',
                       'help': 'Thickness of the flat plate the supports stand on, which sticks to the build plate. '
                               'Thicker is sturdier and easier to remove.'},
 'render_core_groove': {'label': 'Bore grooves',
                        'help': 'Cuts the twisted friction grooves inside the shaft bore. Slow to build, so turn it '
                                'off while iterating.'},
 'resin_detent_clock_offset': {'label': 'Detent support rotation (deg)',
                               'help': 'Rotates the supports under the detent teeth around the ball, so they can land '
                                       'between teeth instead of on them.'},
 'resin_fn': {'label': 'Support facets',
              'help': 'Facet count for the support rods, rafts and breakaway grooves. Higher = smoother but slower.'},
 'resin_support_base_thickness': {'label': 'Support base thickness (mm)',
                                  'help': 'Not used yet: Helios has no generated resin supports, so this has no '
                                          'effect. Add supports in your slicer instead.'},
 'resin_support_contact_radius': {'label': 'Support contact radius (mm)',
                                  'help': 'Not used yet: Helios has no generated resin supports, so this has no '
                                          'effect. Add supports in your slicer instead.'},
 'resin_support_min_height': {'label': 'Support min height (mm)',
                              'help': 'Not used yet: Helios has no generated resin supports, so this has no effect. '
                                      'Add supports in your slicer instead.'},
 'resin_support_rod_thickness': {'label': 'Support rod thickness (mm)',
                                 'help': 'Not used yet: Helios has no generated resin supports, so this has no effect. '
                                         'Add supports in your slicer instead.'},
 'resin_support_spacing': {'label': 'Support spacing (mm)',
                           'help': 'Not used yet: Helios has no generated resin supports, so this has no effect. Add '
                                   'supports in your slicer instead.'},
 'rib_fillet_resin_clearance': {'label': 'Rib fillet support clearance (mm)',
                                'help': "Pulls the rib fillet's corner in by this much to leave room for resin "
                                        'supports.'},
 'rib_flat_bottom': {'label': 'Flat bottom',
                     'help': 'Separate rib part only: builds the drive-pin boss on one side only, so the rib can lie '
                             'flat on the build plate without supports.'},
 'rib_interface_offset_mm': {'label': 'Flange fit clearance (mm)',
                             'help': "Separate rib part only: shrinks the rib's flange so it slides into the shuttle's "
                                     'slot after FDM printing. Raise it if the flange prints too tight; 0 = exact '
                                     'size.'},
 'rib_nub_growth_mm': {'label': 'Nub clearance growth (mm)',
                       'help': "Separate rib part only: enlarges the flange's four nub cutouts so they clear the "
                               "shuttle's nubs. Raise it if they print too tight."},
 'rib_od': {'label': 'Rib diameter (mm)',
            'help': 'Outer diameter of the rounded stiffening rib that braces the spokes to the hub.'},
 'rib_radius': {'label': 'Rib edge radius (mm)', 'help': "Rounding radius of the stiffening rib's outer edge."},
 'rib_thickness': {'label': 'Rib thickness (mm)', 'help': 'Currently has no effect on the geometry.'},
 'rod_count': {'label': 'Rod count',
               'help': 'Number of support rods spaced evenly around the ring. Printed upside down, half this many '
                       'extra rods are also added nearer the top boss.'},
 'rod_od': {'label': 'Rod diameter (mm)',
            'help': 'Thickness of each support rod. Thicker = stiffer support, more resin and cleanup.'},
 'roof_offset': {'label': 'Inner roof peak (mm)',
                 'help': 'How far the inside ceiling of the hollow body peaks upward between hub and outer wall. A '
                         'peaked ceiling prints better than a flat one.'},
 'row_separation_mm': {'label': 'Row spacing (mm)',
                       'help': 'Vertical distance between key rows on the card, used for both top-to-middle and '
                               'middle-to-bottom.'},
 'scale_mm_per_unit': {'label': 'Logo scale (mm per SVG unit)',
                       'help': "Sets the logo's printed size: millimetres per unit in the SVG file. Raise it to make "
                               'the logo bigger.'},
 'shaft_diameter': {'label': 'Shaft diameter (mm)',
                    'help': "Diameter of the shaft hole through the element. Must fit your machine's shaft; adjust "
                            'slightly if the print is too tight or loose.'},
 'shaft_id': {'label': 'Shaft hole diameter (mm)',
              'help': 'Diameter of the hole the element slides onto. Enlarge slightly if prints fit too tightly on '
                      "your machine's post."},
 'shell_size': {'label': 'Min wall thickness (mm)',
                'help': 'Thinnest wall left around the hollow interior of the element. Thicker is stronger and '
                        'heavier; thinner is lighter and uses less resin.'},
 'show_number': {'label': 'Show number label',
                 'help': 'Engraves the pitch number (e.g. 10 or 12) on the top face. Original Selectric I/II and III '
                         'elements have one; Composer elements do not.'},
 'shrinkage_multiplier': {'label': 'Arc shrinkage multiplier',
                          'help': "Scales the shuttle's arc radius to make up for print shrinkage, keeping character "
                                  'spacing along the arc the same. 1.0 = no compensation.'},
 'shuttle_groove_nub_angle': {'label': 'Groove nub angle (deg)',
                              'help': 'Builds without a rib, and the separate rib part: angle between the four '
                                      'retention nubs in the slot. Nubs sit at one and two times this either side of '
                                      'center.'},
 'shuttle_height_offset': {'label': 'Extra shuttle height (mm)',
                           'help': 'Adds height to the top of the shuttle without moving the rib or the characters.'},
 'shuttle_pin_support_base_length': {'label': 'Pin boss base length (mm)',
                                     'help': "Length of the boss's footprint where it meets the rib, toward the "
                                             'shuttle wall.'},
 'shuttle_pin_support_base_width': {'label': 'Pin boss base width (mm)',
                                    'help': "Width of the boss's footprint where it meets the rib."},
 'shuttle_pin_support_height': {'label': 'Pin boss height (mm)',
                                'help': 'How far the raised boss around the drive-pin hole stands up from each face of '
                                        'the rib.'},
 'shuttle_pin_support_height_offset': {'label': 'Pin boss base shift (mm)',
                                       'help': "Shifts the boss's base footprint toward the shuttle wall relative to "
                                               'the hole, tilting the boss sides.'},
 'shuttle_rib_circle': {'label': 'Rib web edge radius (mm)',
                        'help': "Radius of the rib web's gently curved inner edge. Larger = a flatter edge."},
 'shuttle_rib_circle_radius': {'label': 'Rib fillet radius (mm)',
                               'help': "Radius of the rounded corners where the rib web's edge meets the rib band."},
 'shuttle_rib_hump_distance': {'label': 'Rib web inset (mm)',
                               'help': "How far the rib's curved inner edge sits past the line joining the shuttle's "
                                       'two ends. Larger = a narrower rib web.'},
 'shuttle_rib_plane_base': {'label': 'Rib position from top (mm)',
                            'help': 'Distance from the top of the shuttle down to the top face of the internal rib. '
                                    'Real machine measurement - change only if yours differs.'},
 'shuttle_rib_thickness': {'label': 'Rib thickness (mm)',
                           'help': 'Thickness of the flat internal rib that spans the inside of the shuttle. Real '
                                   'machine measurement.'},
 'shuttle_rib_width': {'label': 'Rib band width (mm)',
                       'help': "Width of the rib's band running along the inside of the shuttle wall."},
 'shuttle_square_hole_length': {'label': 'Drive hole length (mm)',
                                'help': 'Length of the square drive-pin hole, toward the shuttle wall.'},
 'shuttle_square_hole_offset': {'label': 'Drive hole inset (mm)',
                                'help': "Distance in from the shuttle's inner wall to the square drive-pin hole "
                                        'through the rib.'},
 'shuttle_square_hole_radius': {'label': 'Drive hole corner radius (mm)',
                                'help': 'Corner rounding of the square drive-pin hole and the boss around it.'},
 'shuttle_square_hole_width': {'label': 'Drive hole width (mm)',
                               'help': 'Width of the square drive-pin hole, across the shuttle.'},
 'shuttle_taper_deg': {'label': 'End chamfer angle (deg)',
                       'help': 'How far, in degrees of arc, the chamfer on each end of the shuttle runs along the '
                               'inside wall.'},
 'shuttle_taper_step': {'label': 'End chamfer depth (mm)',
                        'help': 'How far the chamfer on each end of the shuttle cuts into the wall thickness.'},
 'shuttle_thickness': {'label': 'Shuttle wall thickness (mm)',
                       'help': 'Thickness of the curved shuttle wall. The characters stand out from its outer '
                               'surface.'},
 'side_hole_enabled': {'label': 'Side hole enabled',
                       'help': 'Drills a hole straight through the slug from side to side near the top end, for a pin, '
                               'wire or cord.'},
 'side_hole_fn': {'label': 'Side hole smoothness',
                  'help': 'Number of sides used for the side hole. Higher is rounder but slower.'},
 'side_hole_height_frac': {'label': 'Side hole depth (fraction of body height)',
                           'help': 'How far back from the face the side hole sits, as a fraction of body height: 0 is '
                                   'at the face, 1 is at the base.'},
 'side_hole_id_mm': {'label': 'Side hole diameter (mm)', 'help': 'Diameter of the side-to-side hole.'},
 'size_mm': {'label': 'Font size (mm)',
             'help': "Size of the font's em square. Larger = bigger characters on the element."},
 'skirt_bottom_od': {'label': 'Skirt bottom diameter (mm)',
                     'help': 'Diameter of the skirt at its bottom edge, where the detent teeth are. A real element '
                             'measurement; change it only if yours differs.'},
 'skirt_top_od': {'label': 'Skirt top diameter (mm)',
                  'help': 'Diameter of the tapered skirt below the ball, where it meets the ball. A real element '
                          'measurement; change it only if yours differs.'},
 'snoot_droop_compensation': {'label': 'Hub droop compensation (mm)',
                              'help': 'Print-fit calibration: a printed hub should measure 8.5 mm from its bottom face '
                                      'to the top flat. If yours prints taller, raise this; if shorter, lower it.'},
 'spacing': {'label': 'Support spacing (mm)',
             'help': 'Distance between neighbouring support rods. Smaller = more supports, a firmer hold and more '
                     'cleanup.'},
 'speed_hole_diameter': {'label': 'Speed hole diameter (mm)',
                         'help': 'Diameter of the lightening holes that run through the element top to bottom. Larger '
                                 'holes make a lighter element.'},
 'speed_hole_id': {'label': 'Speed hole diameter (mm)',
                   'help': 'Diameter of the lightening holes through the wheel body. A real machine feature; change it '
                           'only if your machine differs.'},
 'speed_hole_qty': {'label': 'Speed hole count', 'help': 'Number of lightening holes spaced evenly around the wheel.'},
 'speed_hole_quantity': {'label': 'Number of speed holes',
                         'help': 'How many lightening holes are spaced evenly around the element.'},
 'speed_hole_radial': {'label': 'Speed hole distance from center (mm)',
                       'help': "Distance from the wheel's center to the middle of each speed hole."},
 'speed_hole_radius': {'label': 'Speed hole distance from center (mm)',
                       'help': 'Distance from the shaft center to the center of each speed hole.'},
 'sphere_od': {'label': 'Ball diameter (mm)',
               'help': "Diameter of the typeball's spherical body. A real machine measurement; change it only if your "
                       'element differs.'},
 'spoke_chamfer': {'label': 'Spoke flare (mm)', 'help': 'Size of the flare where each spoke meets the type arc.'},
 'spoke_count': {'label': 'Spoke count', 'help': 'Number of spokes joining the hub to the type arc.'},
 'spoke_extent': {'label': 'Spoke spread (deg)',
                  'help': 'Angle from the first spoke to the last; the spokes are spaced evenly within it.'},
 'spoke_height': {'label': 'Spoke height (mm)', 'help': "Height of each spoke's oval cross-section."},
 'spoke_thickness': {'label': 'Spoke thickness (mm)', 'help': "Width of each spoke's oval cross-section."},
 'square_pattern_pitch_mm': {'label': 'Checker square spacing (mm)',
                             'help': 'Center-to-center spacing of the checkerboard squares. Only used when the '
                                     'checkerboard border is on.'},
 'square_pattern_size_mm': {'label': 'Checker square size (mm)',
                            'help': 'Size of each square in the checkerboard border. Only used when the checkerboard '
                                    'border is on.'},
 'start': {'label': 'Sweep start (mm)',
           'help': 'Offset tested in the first column. A negative start tests values both below and above the current '
                   'setting.'},
 'support_groove_thickness': {'label': 'Breakaway web thickness (mm)',
                              'help': 'Cut Groove resin supports only: material left between the two breakaway grooves '
                                      'where the support ring meets the wall. Thicker = sturdier but harder to snap '
                                      'off.'},
 'support_height': {'label': 'Support height (mm)',
                    'help': 'Gap between the element and the support ring it stands on. Taller gives more room to cut '
                            'the supports away.'},
 'support_height_mm': {'label': 'Support height (mm)',
                       'help': 'Gap between the raft and the base of the slug, bridged by the supports.'},
 'support_pitch_mm': {'label': 'Support spacing (mm)',
                      'help': 'Distance between supports along the slug, on both sides of the slot. Smaller means more '
                              'supports.'},
 'support_thickness': {'label': 'Support ring thickness (mm)',
                       'help': 'Thickness of the ring that all the support rods stand on.'},
 'surface_fn': {'label': 'Detail facets',
                'help': 'Facet count for the other round details: hollow interior, speed holes, chamfers. Higher = '
                        'smoother but slower.'},
 'svg_file': {'label': 'Logo SVG file', 'help': 'The vector image to cut into the top face.'},
 'tallen': {'label': 'Tall display type (Plakatschrift)',
            'help': 'Builds the taller display-type variant: adds the extra height below and shifts every character '
                    'row by the baseline offset. Off for a standard element.'},
 'tallen_baseline_offset_mm': {'label': 'Tall type row shift (mm)',
                               'help': 'Moves every character row up or down by this much when tall display type is '
                                       'on. Platen cutout rows are not moved.'},
 'test_char': {'label': 'Test character',
               'help': 'The character struck at every position of the calibration print. Keep it simple and easy to '
                       'read.'},
 'text': {'label': 'Logo text', 'help': 'The text engraved on the top face of the element. Leave blank for no logo.'},
 'text_depth_mm': {'label': 'Logo extrusion depth (mm)',
                   'help': 'How thick the raised logo text is. Thicker text is easier to see and survives the '
                           "chamfer's curve better; too thin and most of it stays buried."},
 'text_offset_deg': {'label': 'Logo letter rotation (deg)',
                     'help': 'Turns each logo character in place. 180 flips the letters so they read from the other '
                             'side.'},
 'text_size_mm': {'label': 'Logo text size (mm)',
                  'help': 'Size of the engraved logo characters. Larger = bigger text.'},
 'text_spacing': {'label': 'Logo letter spacing (deg)',
                  'help': 'Angle between neighboring logo characters around the top face. Larger = more spread out.'},
 'tip_h': {'label': 'Tip length (mm)',
           'help': 'Length of the tapered tip between the support rod and its contact point.'},
 'tip_in': {'label': 'Tip inset (mm)',
            'help': 'How far each support tip sinks into the element, so it fuses on firmly. More = stronger hold, '
                    'bigger mark.'},
 'tip_l': {'label': 'Tip taper length (mm)',
           'help': 'Length over which each rod narrows from rod diameter down to the tip.'},
 'tip_notch_od': {'label': 'Notch support tip diameter (mm)',
                  'help': "Tip diameter for the two supports beside the drive notch, kept small so they don't mar the "
                          'notch.'},
 'tip_notch_offset': {'label': 'Notch support spread (deg)',
                      'help': 'How far either side of the drive notch its two supports are placed, in degrees around '
                              'the shaft.'},
 'tip_od': {'label': 'Tip diameter (mm)',
            'help': "Size of each rod's contact point with the part. Smaller = easier to remove and less marking, but "
                    'weaker hold.'},
 'top_chamfer': {'label': 'Top shaft chamfer (mm)',
                 'help': 'Size of the bevel around the shaft hole on the top face, which eases the element onto the '
                         'post.'},
 'top_countersink_depth': {'label': 'Top countersink depth (mm)',
                           'help': 'Depth of the recess in the top face. A real machine measurement; change it only if '
                                   'your machine differs.'},
 'top_flat_thickness': {'label': 'Top flat thickness (mm)',
                        'help': 'Thickness of the solid top of the ball above the hollow inside. Thicker is stronger '
                                'but heavier.'},
 'top_flat_to_center': {'label': 'Top flat to center (mm)',
                        'help': "Height of the flat top face above the ball's center. A real element measurement; "
                                'change it only if your element differs.'},
 'tube_chamfer': {'label': 'Shaft bore chamfer (mm)', 'help': "Chamfer on the edges of the hub's shaft bore."},
 'type_size_mm': {'label': 'Character size (mm)',
                  'help': 'Size of the characters printed on the card. Unrelated to the font size on the 3D element.'},
 'underscore_lift_mm': {'label': 'Underscore lift (mm)',
                        'help': 'Moves "_" up. Many fonts sink it well below the baseline, which can push it out of '
                                "the character's slot. 0 = font's own position."},
 'upper_char': {'label': 'Upper character',
                'help': 'The character typed with shift. It sits one shift distance above the lower character on the '
                        'same face.'},
 'upper_wing_angle_deg': {'label': 'Wing angle (deg)',
                          'help': 'Tilts the end walls of the slug inward toward the base. On wing slugs this sets the '
                                  'top end; on box slugs it sets both ends. 0 gives square ends.'},
 'vary_baseline': {'label': 'Vary baselines',
                   'help': 'Gives each column a different baseline height so you can see which prints best. Usually '
                           'only this or Vary cutouts is on.'},
 'vary_cutout': {'label': 'Vary cutouts',
                 'help': 'Gives each column a different platen cutout height so you can see which strikes best. '
                         'Usually only this or Vary baselines is on.'},
 'vogue_arrow_svg_file': {'label': 'Vogue arrow SVG file',
                          'help': 'The SVG drawing for the arrow half of the Vogue Foundry mark.'},
 'vogue_enabled': {'label': 'Vogue Foundry mark enabled',
                   'help': 'Adds the two-piece arrow and V mark of the Vogue type foundry. Only used on the Vogue '
                           'Slug.'},
 'vogue_scale_mm_per_unit': {'label': 'Vogue mark scale (mm per SVG unit)',
                             'help': 'Sizes the Vogue Foundry mark: millimeters per unit of its SVG drawings. Separate '
                                     'from the logo scale because the files use very different units.'},
 'vogue_v_svg_file': {'label': 'Vogue V SVG file', 'help': 'The SVG drawing for the V half of the Vogue Foundry mark.'},
 'wall_chamfer': {'label': 'Inner corner chamfer (mm)',
                  'help': 'Size of the angled corners inside the hollow body. Larger chamfers print with less '
                          'overhang.'},
 'wall_min_thickness': {'label': 'Wall thickness (mm)',
                        'help': "Thickness of the hollow body's walls: outer wall, top, bottom and hub. Thicker = "
                                'stronger, heavier, slower to wash out.'},
 'weight_adjustment_mm': {'label': 'Character bolding (mm)',
                          'help': "Thickens (positive) or thins (negative) the card's characters by this much around "
                                  'their outline. 0 leaves them as the font draws them.'},
 'wheel_style': {'label': 'Wheel style',
                 'help': 'Round is a plain body. Notched and Banded give the wall one flat facet per character column, '
                         'with the facet corners falling between columns.'},
 'width_mm': {'label': 'Card width (mm)', 'help': 'Overall width of the index card.'},
 'wing_fn': {'label': 'Wing smoothness',
             'help': 'Number of sides used for the rounded wing ends. Higher is smoother but slower.'},
 'wing_radius_mm': {'label': 'Wing radius (mm)',
                    'help': 'Radius of the rounded ends at the base of the slug, where the wings sit on the typebar.'},
 'wing_thickness_mm': {'label': 'Wing wall thickness (mm)',
                       'help': 'Wall thickness on each side of the typebar slot at the base. The sides taper from the '
                               'full face width down to this.'},
 'wire_thickness_mm': {'label': 'Support wire thickness (mm)',
                       'help': 'Diameter of each support wire. Thicker holds better but leaves bigger marks to clean '
                               'up.'},
 'x_offset_mm': {'label': 'Logo offset (mm)',
                 'help': 'Moves the logo sideways across the top face from the center. Use it to keep the logo clear '
                         'of the shaft and holes.'},
 'x_pos_offset': {'label': 'Horizontal position offset (mm)',
                  'help': 'Shifts every character sideways within its spot on the ball. On the Composer the default is '
                          'print-critical and verified against the original design; leave it unless a test print shows '
                          'drift.'},
 'y_pos_offset': {'label': 'Vertical position offset (mm)',
                  'help': 'Shifts every character up or down within its spot on the ball, moving the baseline. On the '
                          'Composer the default is print-critical and verified against the original design; leave it '
                          'unless a test print shows drift.'},
 'z_exclamation_length_mm': {'label': 'Z-to-! span (mm)',
                             'help': 'Distance from the Z key to the ! key on the bottom row, measured on a real card. '
                                     'Change only if your keyboard differs.'}}

FIELD_TEXT_BY_FAMILY = {
    'cylinder': {},
    'selectric': {'cyl_fn': {'label': 'Bore and platen smoothness',
                'help': "Number of facets on the center shaft hole and on the platen curve cut into each character's face. "
                        'Higher = rounder, slower.'},
     'flatness_tolerance_mm': {'label': 'Flatness tolerance (mm)',
                               'help': 'How closely curved letter outlines are followed when turned into straight '
                                       'segments. Smaller = smoother curves but slower builds.'},
     'min_final_character_diameter': {'label': 'Character tip diameter (mm)',
                                      'help': 'Diameter across two opposing character faces. How far type stands off the '
                                              'ball is half the difference from the ball diameter. Machine measurement; '
                                              'change only if yours differs.'},
     'minkowski_fn': {'label': 'Draft taper smoothness',
                      'help': 'Number of facets on the taper around each character. This is the biggest build-time cost, '
                              'along with flatness tolerance.'},
     'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                           'help': 'The build log warns about downward faces and character rows whose walls rise less than '
                                   'this above horizontal. 30 is a cautious starting point; tune it for your printer and '
                                   'resin.'},
     'platen_diameter': {'label': 'Platen diameter (mm)',
                         'help': 'Diameter of the platen roller; each character face is curved to match it. Selectric I/II '
                                 'and III use 36, Composer 43. Change only if your machine differs.'},
     'resin_fn': {'label': 'Support smoothness',
                  'help': 'Number of facets on the support rafts. Higher = rounder, slower; supports are removed after '
                          'printing, so low values are fine.'},
     'rod_od': {'label': 'Rod diameter (mm)',
                'help': 'Thickness of the support rods and the braces between them. Thicker = stiffer supports that use '
                        'more resin.'},
     'surface_fn': {'label': 'Surface smoothness',
                    'help': 'Number of facets on the ball, skirt, roof and center hub. Higher = smoother surfaces, slower '
                            'builds.'},
     'tip_od': {'label': 'Support tip diameter (mm)',
                'help': "Diameter of each support's tip where it touches the element. Smaller tips leave lighter marks but "
                        'hold less firmly.'}},
    'hammond': {'clip_to_cell': {'label': 'Clip draft to slot',
                      'help': "Trims each character's tapered draft at its own slot so it cannot bleed into the "
                              'neighbouring character. Usually safe to leave off.'},
     'cyl_fn': {'label': 'Body segments',
                'help': "Number of segments used for the body's curved surfaces. Higher = smoother curves but slower "
                        'builds and bigger files.'},
     'flatness_tolerance_mm': {'label': 'Flatness tolerance (mm)',
                               'help': 'How closely character curves are followed when converted to straight segments. '
                                       'Smaller = smoother curves but slower builds.'},
     'font2_chars': {'label': 'Second font characters',
                     'help': 'Characters struck in the second font instead of the main one, for symbols the main typeface lacks.'},
     'font2_path': {'label': 'Second font', 'help': 'Font for the characters listed under Second font characters.'},
     'font2_size_mm': {'label': 'Second font size (mm)', 'help': 'Size of the characters struck in the second font.'},
     'font_path': {'label': 'Label font path',
                   'help': 'Font for the two lines of engraved label text, separate from the font used for the struck '
                           'characters.'},
     'inset': {'label': 'Tip inset (mm)',
               'help': 'How far each support tip sinks into the part surface for a secure bond.'},
     'min_band_height_mm': {'label': 'Min wall band height (mm)',
                            'help': 'The wall is split into horizontal bands to keep the character join clean. Bands are '
                                    'never shorter than this; 0 = automatic. Raise it if the wall mesh is too fine.'},
     'min_final_character_diameter': {'label': 'Character face diameter (mm)',
                                      'help': 'Caliper diameter across two opposite character faces. Characters stand out '
                                              'from the type surface by half the difference, so raising it makes them '
                                              'stand taller.'},
     'min_rod_height': {'label': 'Min rod height (mm)',
                        'help': 'Shortest support rod allowed, which sets the lowest gap between the part and the raft.'},
     'minkowski_cone_height_mm': {'label': 'Draft cone height (mm)',
                                  'help': 'Height of the tapered draft below each character, which roots it into the body. '
                                          'Total depth is face height plus this; lower gives a shallower flare.'},
     'minkowski_fn': {'label': 'Draft cone segments',
                      'help': 'Number of sides on the cone used to taper each character. Higher = smoother sides but much '
                              'slower; only matters when the draft is applied.'},
     'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                           'help': 'The build log flags downward-facing surfaces shallower than this angle above '
                                   'horizontal. Depends on your printer and resin; 30 is a cautious start.'},
     'pre_minkowski_char_height_mm': {'label': 'Character face height (mm)',
                                      'help': 'Height of the straight-sided part of each character; its top is the '
                                              'striking face. Total character depth is this plus the draft cone height.'},
     'raft_od': {'label': 'Raft pad diameter (mm)', 'help': 'Diameter of the foot pad at the bottom of each support rod.'},
     'raft_thickness': {'label': 'Raft thickness (mm)',
                        'help': 'Thickness of the base pad under the supports that sticks to the build plate.'},
     'resin_fn': {'label': 'Support segments',
                  'help': 'Number of sides on each support rod, tip and pad. Higher = rounder supports but slower builds.'},
     'rod_od': {'label': 'Rod diameter (mm)',
                'help': 'Thickness of each support rod. Thicker holds better but is harder to remove.'},
     'surface_fn': {'label': 'Wall segments',
                    'help': "Segment count for the shuttle's outer wall, where the characters join it. Normally kept equal "
                            'to Body segments.'},
     'tip_l': {'label': 'Tip length (mm)', 'help': 'Length of the narrowing section between the rod and its contact tip.'},
     'tip_od': {'label': 'Tip diameter (mm)',
                'help': 'Diameter where each support touches the part. Smaller leaves a smaller mark but holds less '
                        'firmly.'}},
    'mignon_helios': {'circle_segments': {'label': 'Circle smoothness',
                         'help': 'How finely each circle and oval is drawn. Higher is smoother but makes a larger file.'},
     'clip_to_cell': {'label': 'Clip draft to slot',
                      'help': "Trims each character's sloped base at its own slot so it cannot bleed into the next "
                              'character. Leave off for a plain element where it stays buried in the wall anyway.'},
     'core_bottom_offset': {'label': 'Shaft hole bottom offset (mm)',
                            'help': "Raises where the shaft hole's grip zones and bevel start, measured from the bottom "
                                    'face. Estimated value; tune it against your machine.'},
     'core_chamfer': {'label': 'Shaft hole chamfer (mm)',
                      'help': 'Size of the bevel at the ends of the shaft hole, which helps the element slide on. '
                              'Estimated value; tune it against your machine.'},
     'core_contact_length': {'label': 'Shaft grip length (mm)',
                             'help': 'Length of the snug zones at each end of the shaft hole that touch the shaft; the '
                                     'middle is slightly relieved. Estimated value; tune it against your machine.'},
     'core_groove_d': {'label': 'Core groove depth (mm)',
                       'help': 'Size of each twisted friction groove inside the shaft hole. Deeper grooves give a looser '
                               'fit. Estimated value; tune it against your machine.'},
     'core_groove_qty': {'label': 'Core groove count',
                         'help': 'Number of twisted friction grooves inside the shaft hole. Estimated value; tune it '
                                 'against your machine.'},
     'core_web_length': {'label': 'Core slot length (mm)',
                         'help': 'Length of each slot around the shaft hole. Estimated value; tune it against your '
                                 'machine.'},
     'core_web_qty': {'label': 'Core slot count',
                      'help': 'Number of slots cut around the shaft hole. Estimated value; tune it against your machine.'},
     'core_web_width': {'label': 'Core slot width (mm)',
                        'help': 'Width of the slots cut through the wall around the shaft hole, which let it flex onto the '
                                'shaft. Estimated value; tune it against your machine.'},
     'cyl_fn': {'label': 'Shaft bore segments',
                'help': 'How many flat sides make up the round shaft bore. Higher is smoother but slower to build.'},
     'element_diameter': {'label': 'Body diameter (mm)',
                          'help': 'Diameter of the element body the characters stand on. A real machine measurement; '
                                  'change it only if your machine differs.'},
     'element_height': {'label': 'Element height (mm)',
                        'help': 'Overall height of the element. A real machine measurement; change it only if your machine '
                                'differs. On a Mignon, Tallen adds its extra height on top of this.'},
     'flatness_tolerance_mm': {'label': 'Glyph outline accuracy (mm)',
                               'help': "How closely character outlines follow the font's curves. Smaller is smoother but "
                                       'slower to build; larger is faster but more faceted.'},
     'font_path': {'label': 'Logo font', 'help': "Font file used for the raised logo text on the element's top chamfer."},
     'groove_fn': {'label': 'Groove segments',
                   'help': 'How finely each twisted friction groove in the shaft bore is drawn. Higher is smoother but '
                           'slower to build.'},
     'inset': {'label': 'Tip inset (mm)',
               'help': 'How far each rod tip sinks into the element. A little inset gives a stronger hold; 0 just touches '
                       'the surface.'},
     'legend_flatness_tolerance_mm': {'label': 'Character outline accuracy (mm)',
                                      'help': "How closely the card's character outlines follow the font's curves. Smaller "
                                              'is more exact but makes a larger file; a paper card needs little '
                                              'precision.'},
     'legend_font_path': {'label': 'Legend font',
                          'help': "Font for the printed or laser-cut index card. It is separate from the element's font, "
                                  'so any readable face works.'},
     'min_band_height_mm': {'label': 'Min wall band height (mm)',
                            'help': 'The wall is split into horizontal bands so characters join it cleanly. Bands are '
                                    'never shorter than this; 0 = automatic. Raise it if the wall mesh is too fine and '
                                    'slow.'},
     'min_final_character_diameter': {'label': 'Diameter across character faces (mm)',
                                      'help': 'Diameter measured across the striking faces of opposite characters. The '
                                              'difference from the body diameter sets how far characters stand out.'},
     'min_rod_height': {'label': 'Extra rod length (mm)',
                        'help': 'Extends every rod this much further down below the support ring. 0 ends the rods at the '
                                'ring.'},
     'minkowski_cone_height_mm': {'label': 'Draft cone height (mm)',
                                  'help': 'Height of the sloped base under each character that anchors it into the body. '
                                          'Lower it for a shallower flare; the striking face does not move.'},
     'minkowski_fn': {'label': 'Draft cone segments',
                      'help': 'How finely the sloped sides of each character are drawn. This and glyph outline accuracy '
                              'have the biggest effect on build time.'},
     'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                           'help': 'The build log flags downward-facing surfaces shallower than this angle above '
                                   'horizontal, which may print poorly. 30 is a cautious starting point.'},
     'platen_diameter': {'label': 'Platen diameter (mm)',
                         'help': "Diameter of your machine's platen roller. Each character face is curved to match it; "
                                 'change it only if your machine differs.'},
     'platen_fn': {'label': 'Platen segments',
                   'help': 'How many flat sides make up the platen curve cut into each character face. Higher gives a '
                           'smoother curve but builds slower.'},
     'position_offset_deg': {'label': 'Logo position (deg)',
                             'help': 'Rotates the logo around the element. The Label text always sits directly opposite, '
                                     'so moving the logo moves the label too.'},
     'pre_minkowski_char_height_mm': {'label': 'Character face height (mm)',
                                      'help': 'Height of the straight-sided top part of each character, whose top is the '
                                              'striking face. Total character depth is this plus the draft cone height.'},
     'render_core_groove': {'label': 'Core grooves',
                            'help': 'Adds twisted friction grooves inside the shaft bore to help it grip the shaft. Slow '
                                    'to build; turn off for quick test builds.'},
     'resin_fn': {'label': 'Support rod segments',
                  'help': 'How many flat sides make up each round support rod. Higher is smoother but slower to build.'},
     'rod_od': {'label': 'Rod diameter (mm)',
                'help': 'Thickness of each support rod. Thicker rods are sturdier but harder to snap off cleanly.'},
     'surface_fn': {'label': 'Surface segments',
                    'help': "How many flat sides make up the element's other round surfaces, such as the hollow inside and "
                            'the top. Higher is smoother but slower to build.'},
     'text': {'label': 'Logo text',
              'help': 'Text raised in a ring around the top chamfer, such as your name and year. Leave blank for no logo.'},
     'text_size_mm': {'label': 'Logo text size (mm)',
                      'help': 'Height of the logo characters. Keep it small enough that the text fits on the narrow '
                              'chamfer.'},
     'text_spacing': {'label': 'Logo character spacing (deg)',
                      'help': 'Angle between neighbouring logo characters around the ring. Larger spreads the text further '
                              'around the element.'},
     'tip_l': {'label': 'Tip length (mm)', 'help': 'Length of the tapered tip at the top of each rod.'},
     'tip_od': {'label': 'Tip diameter (mm)',
                'help': "Thickness of each rod's tip where it touches the element. Smaller leaves a smaller mark but holds "
                        'less firmly.'}},
    'bennett': {'clip_to_cell': {'label': 'Clip flare to character slot',
                      'help': "Trims each character's tapered flare at its own slot so it cannot bleed into the "
                              'neighboring character. Usually unneeded, since the merged flares stay buried in the wall.'},
     'core_bottom_offset': {'label': 'Core bottom offset (mm)',
                            'help': 'Raises the bottom of the shaft core above the bottom face on some machines. Currently '
                                    'has no effect on the Bennett element.'},
     'core_chamfer': {'label': 'Shaft hole chamfer (mm)',
                      'help': 'Size of the bevel at each end of the shaft hole, which eases sliding the element onto the '
                              'shaft.'},
     'core_contact_length': {'label': 'Shaft contact length (mm)',
                             'help': 'Length at each end of the shaft hole that fits the shaft snugly; the middle is '
                                     'widened to cut friction. Longer gives a steadier fit with more drag.'},
     'core_groove_d': {'label': 'Core groove diameter (mm)',
                       'help': 'Size of each core groove, which also sets how much the middle of the shaft hole is widened '
                               'for relief. Larger reduces friction on the shaft.'},
     'core_groove_qty': {'label': 'Number of core grooves',
                         'help': 'How many twisted friction-relief grooves are cut inside the shaft hole.'},
     'core_web_length': {'label': 'Core window length (mm)',
                         'help': 'Length, along the shaft, of the slot-shaped windows cut through the wall around the '
                                 'shaft hole.'},
     'core_web_qty': {'label': 'Number of core windows',
                      'help': 'How many slot-shaped windows are cut through the wall around the shaft hole, spaced '
                              'evenly.'},
     'core_web_width': {'label': 'Core window width (mm)',
                        'help': 'Width of the slot-shaped windows cut through the wall around the shaft hole.'},
     'cyl_fn': {'label': 'Shaft and pin hole smoothness (segments)',
                'help': 'Number of segments used to draw the shaft hole and positioner pin holes. Higher is rounder and '
                        'more accurate but slower to build.'},
     'depth_mm': {'label': 'Label engraving depth (mm)',
                  'help': 'How deep the label text is cut into the recessed bottom face. Deeper reads better but leaves '
                          'less material under the letters.'},
     'element_diameter': {'label': 'Element diameter (mm)',
                          'help': 'Outer diameter of the element body, not counting the raised characters. A real machine '
                                  'measurement; change it only if your machine differs.'},
     'element_height': {'label': 'Element height (mm)',
                        'help': 'Overall height of the element body. A real machine measurement; change it only if your '
                                'machine differs.'},
     'flatness_tolerance_mm': {'label': 'Glyph curve tolerance (mm)',
                               'help': "How closely character outlines follow the font's true curves. Smaller is smoother "
                                       'but slower to build; larger builds faster with more visible facets.'},
     'font_path': {'label': 'Label font',
                   'help': 'Font used for the name and year engraved into the bottom face of the element. Any TTF or OTF '
                           'file works; a bold face stays legible at small sizes.'},
     'groove_fn': {'label': 'Core groove smoothness (segments)',
                   'help': "Number of segments around each core groove's round profile. Higher is smoother but slower to "
                           'build.'},
     'inset': {'label': 'Support tip overlap (mm)',
               'help': 'How far each support tip sinks into the element so it bonds during printing. More overlap holds '
                       'better but leaves a deeper mark.'},
     'label2': {'label': 'Label 2 (left group)',
                'help': 'Single line of text engraved on the opposite side of the shaft, e.g. a year. Leave blank to skip '
                        'it.'},
     'label_size_mm': {'label': 'Label text size (mm)',
                       'help': 'Height of the engraved label lettering. Larger text is easier to read but must still fit '
                               'inside the recessed bottom face.'},
     'min_band_height_mm': {'label': 'Min wall band height (mm)',
                            'help': 'The body wall is split into horizontal bands so merging the characters in stays '
                                    'clean. Bands are never shorter than this; 0 = automatic. Raise it if the wall mesh is '
                                    'overly fine.'},
     'min_final_character_diameter': {'label': 'Diameter across characters (mm)',
                                      'help': 'Diameter measured across the faces of two opposite characters. Sets how far '
                                              'characters stand proud of the body; change it only if your machine '
                                              'differs.'},
     'minkowski_cone_height_mm': {'label': 'Character flare height (mm)',
                                  'help': 'Height of the tapered base that flares each character into the body. Lower it '
                                          'for a shallower flare; the striking face does not move.'},
     'minkowski_fn': {'label': 'Character flare smoothness (segments)',
                      'help': 'Number of segments in the tapered flare around each character. This and the glyph curve '
                              'tolerance are the biggest build-time levers.'},
     'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                           'help': 'The build log flags downward-facing surfaces shallower than this angle above '
                                   'horizontal. Depends on your printer and resin; 30 is a cautious start.'},
     'platen_diameter': {'label': 'Platen diameter (mm)',
                         'help': "Diameter of the typewriter's platen roller, used to curve each character face to match "
                                 'it. Change it only if your machine differs.'},
     'platen_fn': {'label': 'Platen curve smoothness (segments)',
                   'help': 'Number of segments for the platen-shaped curve cut into each character face. Higher gives a '
                           'smoother striking face but builds slower.'},
     'pre_minkowski_char_height_mm': {'label': 'Character face height (mm)',
                                      'help': 'Height of the straight-sided top of each character, whose top is the '
                                              'striking face. Total character depth is this plus the cone height.'},
     'raft_od': {'label': 'Rod foot diameter (mm)',
                 'help': 'Diameter of the small raft pad at the base of each support rod. Larger feet stick better to the '
                         'build plate.'},
     'render_core_groove': {'label': 'Core grooves',
                            'help': 'Cut twisted friction-relief grooves inside the shaft hole. They are slow to build, so '
                                    'turn off for quick test builds.'},
     'resin_fn': {'label': 'Support smoothness (segments)',
                  'help': 'Number of segments for the resin support ring, rafts and groove. Higher is smoother but slower '
                          'to build; supports rarely need much.'},
     'rod_od': {'label': 'Support rod diameter (mm)',
                'help': 'Thickness of each resin support rod. Thicker rods hold the print more securely but are harder to '
                        'remove and leave bigger marks.'},
     'shaft_diameter': {'label': 'Shaft hole diameter (mm)',
                        'help': 'Diameter of the center hole the element slides onto. Increase slightly if a print is too '
                                'tight on the shaft, decrease if it wobbles.'},
     'support_height': {'label': 'Support height (mm)',
                        'help': 'Gap between the build plate and the element, which sets how tall the support ring and '
                                'rods are. More height leaves more room for removal.'},
     'support_thickness': {'label': 'Support raft thickness (mm)',
                           'help': "Thickness of the support ring's flat base flange and of each rod's foot pad. Thicker "
                                   'is sturdier on the build plate.'},
     'surface_fn': {'label': 'Body smoothness (segments)',
                    'help': 'Number of segments for the outer body, hollow interior, speed holes and countersinks. Higher '
                            'is smoother but slower to build.'},
     'tip_l': {'label': 'Support tip length (mm)',
               'help': 'Length of the tapered section between the rod and its contact tip. Longer tips give a cleaner '
                       'break point.'},
     'tip_od': {'label': 'Support tip diameter (mm)',
                'help': 'Diameter of the narrow tip where each rod touches the element. Smaller tips snap off cleaner but '
                        'hold less firmly.'}},
    'slugs': {'font_path': {'label': 'Copyright font file', 'help': 'The font file used for the engraved side text.'},
     'logo_depth_mm': {'label': 'Logo height (mm)',
                       'help': 'How far the logo stands up from the slug face. Keep it well below the characters so it '
                               'never prints on the paper.'},
     'logo_enabled': {'label': 'Logo enabled',
                      'help': 'Adds a single SVG logo, raised slightly on the slug face between the characters. Off on the '
                              'Vogue and Gauge slugs.'},
     'minkowski_fn': {'label': 'Draft cone smoothness',
                      'help': 'Number of sides on the cone that gives the characters their sloped walls. Higher is '
                              'smoother but builds slower.'},
     'overhang_warn_deg': {'label': 'Overhang warning (deg)',
                           'help': 'The build log flags downward faces, and Selectric glyph rows, shallower than this '
                                   'above horizontal.'},
     'platen_fn': {'label': 'Platen curve smoothness',
                   'help': 'Number of sides used for the platen curve cut into the characters. Higher gives a smoother '
                           'face but builds slower.'},
     'resin_fn': {'label': 'Resin support smoothness',
                  'help': 'Number of sides on the round support wires. Higher is smoother but slower. Not used on box '
                          'slugs, which have no resin supports.'},
     'scale_mm_per_unit': {'label': 'Logo scale (mm per SVG unit)',
                           'help': 'Sizes the logo: millimeters per unit of the SVG drawing. Raise it to make the logo '
                                   'bigger. Each SVG file needs its own value.'},
     'svg_file': {'label': 'Logo SVG file', 'help': 'The SVG drawing used for the logo.'},
     'text': {'label': 'Copyright text',
              'help': 'Text engraved along the side of the slug, such as a copyright line. Its letter size follows the '
                      'typebar slot width. Leave empty for none.'}},
}
