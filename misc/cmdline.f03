! Simple Unix-like command line argument parsing example
!
! modified from: http://jblevins.org/log/cmdline
!
! Fernando Paolo <fpaolo@ucsd.edu>
! February 12, 2011

program main
   implicit none

   character(100) :: arg, arg_a, arg_b
   character(*), parameter :: arg_c = 'Hello!'
   logical :: jump = .false.
   integer :: i

   call get_arguments()

contains

   subroutine get_arguments()
      if (command_argument_count() < 1) call print_help()

      do i = 1, command_argument_count()  ! iterate over arguments
         if (jump) then                   ! jump one iteration
             jump = .false.
             cycle
         endif
         call get_command_argument(i, arg)

         select case (arg)
            case ('-h', '--help')
               call print_help()
            case ('-a')
               call get_command_argument(i+1, arg_a)
               if (arg_a(:1) == '-' .or. arg_a == '') call print_help()  ! check the arg is correct
               print '(a)', trim(arg_a)
               jump = .true.
            case ('-b')
               call get_command_argument(i+1, arg_b)
               if (arg_b(:1) == '-' .or. arg_b == '') call print_help()
               print '(a)', trim(arg_b)
               jump = .true.
            case ('-c')
               print '(a)', arg_c
            case default
               print '(a,a,/)', 'unrecognized command line option: ', trim(arg)
               call print_help()
         endselect
      enddo
   end subroutine get_arguments

   subroutine print_help()
      print '(a)', 'usage: ./thisprog [-h] [-a ARG_A] [-b ARG_B] [-c]'
      print '(a)', ''
      print '(a)', 'options:'
      print '(a)', '  -h, --help  print the help message and exit'
      print '(a)', '  -a ARG_A    print the argument ARG_A'
      print '(a)', '  -b ARG_B    print the argument ARG_B'
      print '(a)', '  -c          print the default argument for -c'
      stop
   end subroutine print_help

end program main
