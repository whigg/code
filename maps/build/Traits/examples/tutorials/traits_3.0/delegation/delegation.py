#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(Delegation Fixes and Improvements)------------------------------------------
"""
Delegation Fixes and Improvements
=================================

In previous versions of Traits there were a number of problems (i.e. bugs) in
the delegation support that made delegation virtually unusable in some 
situations.

As a result, one of the primary goals of Traits 3.0 was to fix all known 
problems with delegation, thus allowing it to reclaim its role as one of the 
five keys pillars of the Traits package (those pillars being *initialization*, 
*validation*, *notification*, *delegation* and *visualization*).

We are happy to report that not only have all known bugs been fixed, but a 
previously unsupported, though often requested, feature has been added as well.

Delegation Event Notification
-----------------------------

Previously, many Traits users implicitly assumed that changes made to a
*delegatee* trait would generate a change notification on any *delegater* trait
(no matter how many such traits there might be). Unfortunately, this was not
the case.

However, starting with Traits 3.0, this feature has now been implemented. An
example of what this means is shown below::
    
    class Parent ( HasTraits ):
        
        first_name = Str
        last_name  = Str
        
    class Child ( HasTraits ):
        
        mother = Instance( Parent )
        father = Instance( Parent )
        
        first_name = Str
        last_name  = Delegate( 'father' )
        
In this example, we've created two classes, **Parent** and **Child**, and the
value of the **Child** class's *last_name* trait delegates its value to its
*father* object's *last_name* trait.

Next, we'll set up a simple set of test objects::
        
    mom = Parent( first_name = 'Julia', last_name = 'Wilson' )
    dad = Parent( first_name = 'William', last_name = 'Chase' )        
    son = Child( mother = mom, father = dad, first_name = 'John' )
    
Finally, we'll set up a notification handler on the *son* object's *last_name*
trait and then try out various combinations of setting both the *father* and
*son* object's *last_name* trait to see in which cases the notification handler
is called::

    def name_changed ( name ):
        print 'Your last name has been changed to %s.' % name
        
    # Set up a change notification handler on the son's last name:    
    son.on_trait_change( name_changed, 'last_name' )
    
    # This should cause the son's last name to change as well:
    print "Changing dad's last name to Jones."
    dad.last_name = 'Jones'
    
    # This change override's the father's last name for the son:
    print "Changing son's last name to Thomas."
    son.last_name = 'Thomas'
    
    # This should no longer have any effect on the son's last name:
    print "Changing dad's last name to Riley."
    dad.last_name = 'Riley'
    
    # Son decide's to revert his name back to his father's name:
    print "Reverting son's last name."
    del son.last_name
    
    # Now changing the father's name should affect the son again:
    print "Changing dad's last name to Simmons."
    dad.last_name = 'Simmons'
    
For the actual results of running this code, refer to the **Output** tab. Note
that for each case in which an explicit or implicit change is made to the *son*
object's *last_name* trait, a corresponding call is made to the change
notification handler.

Also, please take a look at the **ChildController** class and the **Demo** tab 
for an example of using delegated traits in a Traits user interface.
"""

#--<Imports>--------------------------------------------------------------------

from enthought.traits.api import *
from enthought.traits.ui.api import *

#--[Parent Class]---------------------------------------------------------------
    
class Parent ( HasTraits ):
    
    first_name = Str
    last_name  = Str
    
    view = View( 
        Item( 'first_name' ),
        Item( 'last_name' ),
        resizable = True
    )

#--[Child Class]----------------------------------------------------------------

class Child ( HasTraits ):
    
    mother = Instance( Parent )
    father = Instance( Parent )
    
    first_name = Str
    last_name  = Delegate( 'father' )

#--[ChildController Class]------------------------------------------------------

class ChildController ( Controller ):

    reset = Button( 'Reset Last Name' )
    
    view = View(
        VGroup(
            VGroup( 
                Item( 'father', style = 'custom' ),
                label       = 'Father',
                show_labels = False,
                show_border = True
            ),
            VGroup(
                Item( 'mother', style = 'custom' ),
                label       = 'Mother',
                show_labels = False,
                show_border = True
            ),
            VGroup(
                Item( 'first_name' ),
                HGroup(
                    Item( 'last_name', springy = True ),
                    Item( 'controller.reset', show_label = False ),
                ),
                label       = 'Child',
                show_border = True
            )
        ),
        resizable = True
    )
    
    def _reset_changed ( self ):
        """ Reset the child's last name."""
        del self.model.last_name

#--[Example*]-------------------------------------------------------------------

mom = Parent( first_name = 'Julia', last_name = 'Wilson' )
dad = Parent( first_name = 'William', last_name = 'Chase' )        
son = Child( mother = mom, father = dad, first_name = 'John' )

def name_changed ( name ):
    print 'Your last name has been changed to %s.' % name
    
# Set up a change notification handler on the son's last name:    
son.on_trait_change( name_changed, 'last_name' )

# This should cause the son's last name to change as well:
print "Changing dad's last name to Jones."
dad.last_name = 'Jones'

# This change override's the father's last name for the son:
print "Changing son's last name to Thomas."
son.last_name = 'Thomas'

# This should no longer have any effect on the son's last name:
print "Changing dad's last name to Riley."
dad.last_name = 'Riley'

# Son decide's to revert his name back to his father's name:
print "Reverting son's last name."
del son.last_name

# Now changing the father's name should affect the son again:
print "Changing dad's last name to Simmons."
dad.last_name = 'Simmons'

#--<Demo>-----------------------------------------------------------------------

demo = ChildController(
           model = Child( mother = mom, father = dad, first_name = 'Rachel' ) )
